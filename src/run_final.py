"""Avaliação final da M3, em duas etapas separadas para que o teste não oriente nenhuma escolha.

    python src/run_final.py --etapa desenvolvimento
    python src/run_final.py --etapa teste

Desenvolvimento (dias já usados na M2, manhã e tarde):
- busca em grade de alpha e free_max (referência adaptativa) e de tau, para cada variante;
- validação cruzada deixando um dia de fora (estimativa fora da amostra no desenvolvimento);
- treino da regressão logística e escolha do sistema final pelo F1 da validação cruzada;
- grava `models/sistema_final_m3.json` (parâmetros congelados e modelo).

Teste (dias inéditos, de 06:25 a 18:35): lê os parâmetros congelados, avalia uma única vez o
baseline da M2, as variantes da M3 e a reavaliação das configurações A e C da M2.

Configuração: `configs/experimento_m3.json`. Os dados de teste e as tardes do desenvolvimento
são obtidos com `python src/get_data.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from parking import visualize as viz
from parking.classifier import LogisticModel
from parking.dataset import Frame, load_spaces, parse_frame
from parking.experiment import REPO_ROOT, load_experiment, load_reference, read_image, resolve, write_csv
from parking.metrics import classification_metrics, count_metrics, sweep_f1
from parking.pipeline import PipelineConfig, Reference, analyze, preprocess
from parking.sequence import DayProcessor, SequenceConfig

DEFAULT_EXPERIMENT = REPO_ROOT / "configs" / "experimento_m3.json"
FROZEN = REPO_ROOT / "models" / "sistema_final_m3.json"
BASELINE = "B_M2"


# ------------------------------------------------------------------ dados


class Dataset:
    """Quadros por divisão (desenvolvimento/teste), rótulos e referências do dia."""

    def __init__(self, experiment: dict):
        self.experiment = experiment
        self.root = resolve(experiment["dataset_root"])
        self.reference_paths = {d: resolve(p) for d, p in experiment["references"].items()}
        self.reference_ids = {p.stem for p in self.reference_paths.values()}
        self.frames = {split: self._list(folders) for split, folders in experiment["splits"].items()}
        self._labels: dict[str, dict[int, int | None]] = {}
        self._references: dict = {}

    def _list(self, folders: list[str]) -> list[Frame]:
        frames = []
        for folder in folders:
            jpgs = sorted((self.root / folder).glob("*.jpg"))
            if not jpgs:
                raise SystemExit(f"Sem imagens em {self.root / folder}. Rode antes: python src/get_data.py")
            frames += [parse_frame(p) for p in jpgs]
        return sorted(frames, key=lambda f: (f.date, f.time))

    def days(self, split: str) -> list[str]:
        return sorted({f.date for f in self.frames[split]})

    def day_frames(self, split: str, date: str) -> list[Frame]:
        return [f for f in self.frames[split] if f.date == date and f.id not in self.reference_ids]

    def labels(self, frame: Frame) -> dict[int, int | None]:
        if frame.id not in self._labels:
            self._labels[frame.id] = {s.id: s.occupied for s in load_spaces(frame.xml_path)}
        return self._labels[frame.id]

    def reference(self, date: str, cfg: PipelineConfig) -> Reference:
        key = (date, cfg.blur_ksize)
        if key not in self._references:
            self._references[key] = load_reference(self.reference_paths[date], cfg)
        return self._references[key]

    def manifest(self) -> list[dict]:
        out = []
        for split, frames in self.frames.items():
            for f in frames:
                labels = self.labels(f)
                out.append(
                    {
                        "frame_id": f.id,
                        "condition": f.condition,
                        "date": f.date,
                        "time": f.time,
                        "split": "referencia" if f.id in self.reference_ids else split,
                        "spaces": len(labels),
                        "occupied": sum(v == 1 for v in labels.values()),
                        "unlabeled": sum(v is None for v in labels.values()),
                        "path": f.path.relative_to(REPO_ROOT).as_posix(),
                    }
                )
        return out


# ------------------------------------------------------------------ execução das sequências

Spec = tuple[PipelineConfig, SequenceConfig]


def run_sequences(data: Dataset, split: str, specs: dict[str, Spec], compact: bool = False,
                  snapshots: dict | None = None) -> dict[str, list]:
    """Processa cada dia da divisão, em ordem, com todos os `specs` ao mesmo tempo.

    Cada imagem é lida uma vez; a análise contra a referência fixa é compartilhada entre os
    specs que usam a mesma configuração. Com `compact`, guarda só (dia, escore, rótulo).
    `snapshots` = {frame_id: nome do spec} guarda a referência adaptativa e as etapas daquele quadro.
    """
    out: dict[str, list] = {name: [] for name in specs}
    for date in data.days(split):
        procs = {name: DayProcessor(data.reference(date, cfg), cfg, seq) for name, (cfg, seq) in specs.items()}
        for frame in data.day_frames(split, date):
            labels = data.labels(frame)
            image = read_image(frame.path)
            grays, fixed = {}, {}
            for name, (cfg, seq) in specs.items():
                if cfg.blur_ksize not in grays:
                    grays[cfg.blur_ksize] = preprocess(image, cfg)
                gray = grays[cfg.blur_ksize]
                keep = snapshots is not None and snapshots.get(frame.id) == name
                fixed_result = None
                if seq.use_fixed and not keep:
                    if cfg not in fixed:
                        fixed[cfg] = analyze(gray, procs[name].fixed, cfg)
                    fixed_result = fixed[cfg]
                if keep:
                    snapshots[frame.id] = {
                        "spec": name,
                        "image": image,
                        "gray": gray,
                        "fixed": procs[name].fixed.gray,
                        "adaptive": procs[name].adaptive_reference().gray,
                    }
                rows, steps = procs[name].step(gray, keep_steps=keep, fixed_result=fixed_result)
                if keep:
                    snapshots[frame.id]["steps"] = steps
                    snapshots[frame.id]["rows"] = rows
                for r in rows:
                    label = labels.get(r["space_id"])
                    if label is None:
                        continue  # vaga sem rótulo no XML: fora da avaliação (como na M2)
                    if compact:
                        out[name].append((frame.date, r["score"], label))
                    else:
                        out[name].append(
                            {"frame_id": frame.id, "date": frame.date, "condition": frame.condition,
                             "time": frame.time, **r, "label": label}
                        )
    return out


def _worker(job: tuple) -> dict[str, list]:
    experiment, split, specs, compact = job
    return run_sequences(Dataset(experiment), split, specs, compact=compact)


def run_parallel(experiment: dict, split: str, specs: dict[str, Spec], compact: bool, workers: int) -> dict[str, list]:
    """Divide os specs entre processos (cada um lê as imagens por conta própria)."""
    names = list(specs)
    workers = max(1, min(workers, len(names)))
    if workers == 1:
        return run_sequences(Dataset(experiment), split, specs, compact=compact)
    jobs = [(experiment, split, {n: specs[n] for n in names[i::workers]}, compact) for i in range(workers)]
    out: dict[str, list] = {}
    with ProcessPoolExecutor(workers) as pool:
        for part in pool.map(_worker, jobs):
            out.update(part)
    return {n: out[n] for n in names}


# ------------------------------------------------------------------ ajuste


def taus_from(spec: dict) -> np.ndarray:
    return np.round(np.arange(spec["start"], spec["stop"] + 1e-9, spec["step"]), 4)


def tune_threshold(scores, labels, taus: np.ndarray, minimum: float = 0.0) -> dict:
    """Maior F1; em empate, tau = mediana da faixa de ótimos (mesmo critério da M2)."""
    taus = taus[taus >= minimum - 1e-9]
    f1 = sweep_f1(scores, labels, taus)
    best = float(f1.max())
    plateau = taus[np.isclose(f1, best)]
    return {"f1": best, "tau": float(np.round(np.median(plateau), 2)), "tau_min": float(plateau.min()),
            "tau_max": float(plateau.max()), "n_optimal": int(plateau.size)}


def select(candidates: list[dict]) -> dict:
    return max(candidates, key=lambda c: (round(c["f1"], 6), c["n_optimal"]))


def grid_specs(experiment: dict, cfg: PipelineConfig) -> dict[str, tuple[str, Spec, dict]]:
    """Todas as combinações a testar: nome -> (variante, spec, parâmetros)."""
    search = experiment["busca"]
    specs = {}
    for variant, v in experiment["variantes"].items():
        if not v["use_adaptive"]:
            seq = SequenceConfig(use_fixed=True, use_adaptive=False)
            specs[variant] = (variant, (cfg, seq), {"alpha": None, "free_max": 0.0})
            continue
        for alpha in search["alpha"]:
            for free_max in search["free_max"]:
                seq = SequenceConfig(use_fixed=v["use_fixed"], use_adaptive=True, alpha=alpha, free_max=free_max)
                specs[f"{variant}|{alpha}|{free_max}"] = (variant, (cfg, seq), {"alpha": alpha, "free_max": free_max})
    return specs


def as_arrays(compact: list) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dates = np.array([c[0] for c in compact])
    return dates, np.array([c[1] for c in compact], float), np.array([c[2] for c in compact], int)


def predictions_by_rule(rows: list[dict], tau: float) -> list[int]:
    return [int(r["score"] >= tau) for r in rows]


# ------------------------------------------------------------------ métricas


def group_metrics(rows: list[dict], predicted: list[int], groups: list[tuple[str, callable]]) -> list[dict]:
    out = []
    for name, keep in groups:
        idx = [i for i, r in enumerate(rows) if keep(r)]
        if not idx:
            continue
        per_frame = defaultdict(lambda: [0, 0, 0])
        for i in idx:
            per_frame[rows[i]["frame_id"]][0] += rows[i]["label"]
            per_frame[rows[i]["frame_id"]][1] += predicted[i]
            per_frame[rows[i]["frame_id"]][2] += 1
        counts = np.array(list(per_frame.values()))
        out.append(
            {
                "group": name,
                **classification_metrics([rows[i]["label"] for i in idx], [predicted[i] for i in idx]),
                **count_metrics(counts[:, 0], counts[:, 1], 40),
            }
        )
    return out


def standard_groups(rows: list[dict], prefix: str) -> list[tuple[str, callable]]:
    days = sorted({r["date"] for r in rows})
    conditions = [c for c in ("Sunny", "Cloudy", "Rainy") if any(r["condition"] == c for r in rows)]
    segments = sorted({(r["date"], r["condition"]) for r in rows})
    groups = [(f"{prefix} · dia {d}", lambda r, d=d: r["date"] == d) for d in days]
    groups += [(f"{prefix} · {d} ({c})", lambda r, d=d, c=c: r["date"] == d and r["condition"] == c) for d, c in segments]
    groups += [(f"{prefix} · condição {c}", lambda r, c=c: r["condition"] == c) for c in conditions]
    groups += [(f"{prefix} · total", lambda r: True)]
    return groups


def fixed_broken(rows: list[dict], base: list[int], variant: list[int]) -> dict:
    fixed = sum((b != r["label"]) and (v == r["label"]) for r, b, v in zip(rows, base, variant))
    broken = sum((b == r["label"]) and (v != r["label"]) for r, b, v in zip(rows, base, variant))
    return {"fixed": int(fixed), "broken": int(broken)}


# ------------------------------------------------------------------ formatação


def fmt(value, digits: int = 3) -> str:
    if isinstance(value, (float, np.floating)):
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")
    return str(value)


def markdown_table(header: list[str], rows: list[list], digits: int = 3) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(fmt(v, digits) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def crop_box(region, shape, margin: int = 14) -> tuple[int, int, int, int]:
    x, y, w, h = region.bbox
    height, width = shape[:2]
    return max(x - margin, 0), max(y - margin, 0), min(x + w + margin, width), min(y + h + margin, height)


def crop(img: np.ndarray, region, box) -> np.ndarray:
    x0, y0, x1, y1 = box
    out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img.copy()
    cv2.polylines(out, [region.contour], True, (214, 120, 42), 1, cv2.LINE_AA)
    return out[y0:y1, x0:x1]


# ------------------------------------------------------------------ etapa 1: desenvolvimento


def stage_development(experiment: dict, data: Dataset, out_dir: Path, workers: int) -> None:
    cfg = PipelineConfig.from_dict(experiment["pipeline"])
    taus = taus_from(experiment["busca"]["tau"])
    days = data.days("desenvolvimento")
    write_csv(out_dir / "manifesto_imagens.csv", data.manifest())

    # 1) Busca em grade: todas as combinações em uma única passada pelos quadros.
    grid = grid_specs(experiment, cfg)
    print(f"Desenvolvimento: {len(grid)} combinações em {len(days)} dias ({workers} processos) ...", flush=True)
    compact = run_parallel(experiment, "desenvolvimento", {k: spec for k, (_, spec, _) in grid.items()}, True, workers)

    grid_rows, best = [], {}
    per_variant = defaultdict(list)
    for key, (variant, (_, seq), params) in grid.items():
        dates, scores, labels = as_arrays(compact[key])
        tuned = tune_threshold(scores, labels, taus, params["free_max"])
        entry = {"key": key, "variant": variant, **params, **tuned}
        per_variant[variant].append(entry)
        grid_rows.append({k: v for k, v in entry.items() if k != "key"})
    for variant, entries in per_variant.items():
        best[variant] = select(entries)
    write_csv(out_dir / "grade_ajuste.csv", grid_rows)

    # 2) Validação cruzada deixando um dia de fora (regras): ajuste em 2 dias, avaliação no 3º.
    cv_pred = defaultdict(dict)  # variante -> dia -> (escores, rótulos, previsões)
    cv_choice = defaultdict(dict)  # variante -> dia -> combinação escolhida
    for held in days:
        for variant, entries in per_variant.items():
            candidates = []
            for e in entries:
                dates, scores, labels = as_arrays(compact[e["key"]])
                train = dates != held
                candidates.append({**e, **tune_threshold(scores[train], labels[train], taus, e["free_max"])})
            choice = select(candidates)
            dates, scores, labels = as_arrays(compact[choice["key"]])
            test = dates == held
            cv_choice[variant][held] = choice
            cv_pred[variant][held] = (labels[test], (scores[test] >= choice["tau"]).astype(int))

    # 3) Linhas completas das combinações necessárias (escolhidas no ajuste e em cada dobra).
    needed = {best[v]["key"] for v in best} | {c["key"] for v in cv_choice for c in cv_choice[v].values()}
    snap_day = "2013-04-14"
    snap_ids = [f.id for f in data.day_frames("desenvolvimento", snap_day)
                if f.time[:5] in ("12:00", "16:45", "17:00")]
    full = run_parallel(experiment, "desenvolvimento", {k: grid[k][1] for k in needed}, False, workers)
    snapshots = {fid: best["dupla"]["key"] for fid in snap_ids}
    run_sequences(data, "desenvolvimento", {best["dupla"]["key"]: grid[best["dupla"]["key"]][1]}, compact=True,
                  snapshots=snapshots)

    # 4) Regressão logística sobre os descritores da variante base, com a mesma validação cruzada.
    clf = experiment["classificador"]
    feats, lam = clf["features"], clf["lam"]
    lr_cv = {}
    for held in days:
        key = cv_choice[clf["base"]][held]["key"]
        train = [r for r in full[key] if r["date"] != held]
        test = [r for r in full[key] if r["date"] == held]
        model = LogisticModel.fit(train, feats, lam)
        model.threshold = tune_threshold(model.proba(train), [r["label"] for r in train], taus)["tau"]
        lr_cv[held] = ([r["label"] for r in test], model.predict(test).tolist(), model.threshold)
    base_rows = full[best[clf["base"]]["key"]]
    model = LogisticModel.fit(base_rows, feats, lam)
    model.threshold = tune_threshold(model.proba(base_rows), [r["label"] for r in base_rows], taus)["tau"]

    # 5) Escolha do sistema final pelo F1 da validação cruzada (empate: a regra, mais simples).
    def pooled(pred_by_day: dict) -> dict:
        labels = np.concatenate([np.asarray(pred_by_day[d][0]) for d in days])
        preds = np.concatenate([np.asarray(pred_by_day[d][1]) for d in days])
        return classification_metrics(labels, preds)

    cv_summary = {v: pooled(cv_pred[v]) for v in per_variant}
    cv_summary[clf["nome"]] = pooled(lr_cv)
    final = clf["nome"] if cv_summary[clf["nome"]]["f1"] > cv_summary[clf["base"]]["f1"] else clf["base"]

    cv_rows = []
    for name in list(per_variant) + [clf["nome"]]:
        for held in days:
            labels, preds = (lr_cv[held][:2] if name == clf["nome"] else cv_pred[name][held])
            m = classification_metrics(labels, preds)
            choice = cv_choice[clf["base"] if name == clf["nome"] else name][held]
            cv_rows.append({"variante": name, "dia_avaliado": held, "alpha": choice["alpha"], "free_max": choice["free_max"],
                            "limiar": lr_cv[held][2] if name == clf["nome"] else choice["tau"], **m})
        cv_rows.append({"variante": name, "dia_avaliado": "todos (agregado)", "alpha": None, "free_max": None,
                        "limiar": None, **cv_summary[name]})
    write_csv(out_dir / "validacao_cruzada.csv", cv_rows)

    # 6) Desempenho no próprio desenvolvimento (dentro da amostra), por segmento.
    dev_metrics = []
    for variant, b in best.items():
        rows = full[b["key"]]
        dev_metrics += [{"variante": variant, **m} for m in group_metrics(rows, predictions_by_rule(rows, b["tau"]),
                                                                          standard_groups(rows, "dev"))]
    dev_metrics += [{"variante": clf["nome"], **m} for m in group_metrics(base_rows, model.predict(base_rows).tolist(),
                                                                          standard_groups(base_rows, "dev"))]
    write_csv(out_dir / "metricas_desenvolvimento.csv", dev_metrics)

    # 7) Congela tudo o que a etapa de teste vai usar.
    frozen = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "commit_do_codigo": git_commit(),
        "dias_de_desenvolvimento": days,
        "pipeline": asdict(cfg),
        "variantes": {
            v: {"descricao": experiment["variantes"][v]["descricao"],
                **asdict(grid[b["key"]][1][1]), "tau": b["tau"], "f1_desenvolvimento": b["f1"],
                "faixa_tau": [b["tau_min"], b["tau_max"]]}
            for v, b in best.items()
        },
        "classificador": {"nome": clf["nome"], "descricao": clf["descricao"], "base": clf["base"], **model.to_dict()},
        "final": final,
        "criterio_final": "maior F1 agregado na validação cruzada por dia do desenvolvimento "
                          "(regra da variante dupla x regressão logística; empate favorece a regra)",
        "f1_validacao_cruzada": {k: v["f1"] for k, v in cv_summary.items()},
    }
    FROZEN.parent.mkdir(parents=True, exist_ok=True)
    with open(FROZEN, "w", encoding="utf-8") as f:
        json.dump(frozen, f, indent=2, ensure_ascii=False)

    # 8) Figuras do desenvolvimento.
    grids = {}
    search = experiment["busca"]
    for variant, entries in per_variant.items():
        if entries[0]["alpha"] is None:
            continue
        values = [[next(e["f1"] for e in entries if e["alpha"] == a and e["free_max"] == fm) for fm in search["free_max"]]
                  for a in search["alpha"]]
        chosen = (search["alpha"].index(best[variant]["alpha"]), search["free_max"].index(best[variant]["free_max"]))
        grids[variant] = {"f1": values, "alpha": search["alpha"], "free_max": search["free_max"], "chosen": chosen}
    viz.plot_grid_f1(grids, out_dir / "fig_grade_ajuste.png")
    viz.plot_coefficients(dict(zip(model.features, model.weights[1:].tolist())), out_dir / "fig_coeficientes_lr.png")

    panels = []
    reference = data.reference(snap_day, cfg)
    for fid in snap_ids:
        s = snapshots[fid]
        if isinstance(s, dict):
            hhmm = fid[11:16].replace("_", ":")
            panels += [(f"Quadro atual {hhmm}", s["image"]), (f"Referência adaptativa antes de {hhmm}", s["adaptive"]),
                       (f"|atual − adaptativa| {hhmm}", viz.diff_view(s["steps"]["ad"]["diff"]))]
    panels = [("Referência fixa (06:40)", reference.gray), ("", np.full_like(reference.gray, 252)),
              ("", np.full_like(reference.gray, 252))] + panels
    viz.save_panel(panels, out_dir / "fig_referencia_adaptativa.jpg")

    # 9) Resumo em Markdown.
    md = ["# Desenvolvimento da M3 (gerado por `src/run_final.py --etapa desenvolvimento`)", ""]
    md += ["Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.", ""]
    md += [f"Dias de desenvolvimento: {', '.join(days)} ({sum(len(data.day_frames('desenvolvimento', d)) for d in days)} quadros avaliados).", ""]
    md += ["## Parâmetros escolhidos (ajuste em todo o desenvolvimento)", ""]
    md.append(markdown_table(
        ["Variante", "alpha", "free_max", "τ", "faixa de τ ótimos", "F1 (dentro da amostra)"],
        [[v, fmt(b["alpha"], 2) if b["alpha"] is not None else "—", fmt(b["free_max"], 2) if b["alpha"] is not None else "—",
          fmt(b["tau"], 2), f"{fmt(b['tau_min'], 2)} – {fmt(b['tau_max'], 2)}", b["f1"]] for v, b in best.items()]))
    md += ["", f"Regressão logística ({clf['nome']}): λ = {fmt(lam, 1)}, limiar de probabilidade = {fmt(model.threshold, 2)}.", ""]
    md.append(markdown_table(["Descritor", "Peso (padronizado)"],
                             [[k, v] for k, v in zip(model.features, model.weights[1:].tolist())]))
    md += ["", "## Validação cruzada deixando um dia de fora (fora da amostra)", ""]
    md.append(markdown_table(
        ["Variante", "Dia avaliado", "alpha", "free_max", "Limiar", "VP", "FP", "FN", "VN", "F1", "Especificidade"],
        [[r["variante"], r["dia_avaliado"], "—" if r["alpha"] is None else fmt(r["alpha"], 2),
          "—" if r["free_max"] is None else fmt(r["free_max"], 2), "—" if r["limiar"] is None else fmt(r["limiar"], 2),
          r["tp"], r["fp"], r["fn"], r["tn"], r["f1"], r["specificity"]] for r in cv_rows]))
    md += ["", f"**Sistema final escolhido:** `{final}` ({frozen['criterio_final']}).", ""]
    md += ["## Desempenho dentro da amostra, por grupo", ""]
    md.append(markdown_table(
        ["Variante", "Grupo", "n", "FP", "FN", "F1", "Especificidade", "EMA contagem"],
        [[m["variante"], m["group"], m["n"], m["fp"], m["fn"], m["f1"], m["specificity"], m["count_mae"]] for m in dev_metrics]))
    md.append("")
    (out_dir / "resultados_desenvolvimento.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Parâmetros congelados em {FROZEN.relative_to(REPO_ROOT).as_posix()} (final: {final}).")
    print(f"Resumo em {(out_dir / 'resultados_desenvolvimento.md').relative_to(REPO_ROOT).as_posix()}")


# ------------------------------------------------------------------ etapa 2: teste


def load_frozen() -> dict:
    if not FROZEN.exists():
        raise SystemExit(f"{FROZEN.relative_to(REPO_ROOT)} não existe: rode antes --etapa desenvolvimento.")
    with open(FROZEN, encoding="utf-8") as f:
        return json.load(f)


def frozen_specs(frozen: dict) -> dict[str, tuple[Spec, float]]:
    cfg = PipelineConfig.from_dict(frozen["pipeline"])
    return {name: ((cfg, SequenceConfig.from_dict(v)), v["tau"]) for name, v in frozen["variantes"].items()}


def stage_test(experiment: dict, data: Dataset, out_dir: Path, workers: int) -> None:
    frozen = load_frozen()
    m2 = load_experiment(experiment["m2"]["experimento"])
    clf = frozen["classificador"]
    model = LogisticModel.from_dict(clf)
    final = frozen["final"]
    write_csv(out_dir / "manifesto_imagens.csv", data.manifest())

    # Especificações: baseline e reavaliação da M2 (referência fixa, parâmetros da M2) + variantes da M3.
    only_fixed = SequenceConfig(use_fixed=True, use_adaptive=False)
    m2_names = {BASELINE: experiment["m2"]["baseline"], **{m2_name(n): n for n in experiment["m2"]["reavaliar"]}}
    specs: dict[str, Spec] = {}
    taus: dict[str, float] = {}
    for short, name in m2_names.items():
        cfg = PipelineConfig.from_dict(m2["configs"][name])
        specs[short] = (cfg, only_fixed)
        taus[short] = cfg.occupancy_threshold
    for name, (spec, tau) in frozen_specs(frozen).items():
        specs[name] = spec
        taus[name] = tau

    days = data.days("teste")
    print(f"Teste: {len(specs)} configurações em {len(days)} dias inéditos ({', '.join(days)}) ...", flush=True)
    rows = run_parallel(experiment, "teste", specs, False, workers)

    # Todas as configurações percorrem as mesmas vagas-quadro, na mesma ordem.
    order = [(r["frame_id"], r["space_id"]) for r in rows[BASELINE]]
    assert all([(r["frame_id"], r["space_id"]) for r in rows[n]] == order for n in rows)
    ref_rows = rows[BASELINE]
    predicted = {name: predictions_by_rule(rows[name], taus[name]) for name in specs}
    predicted[clf["nome"]] = model.predict(rows[clf["base"]]).tolist()
    probabilities = model.proba(rows[clf["base"]])
    names = [BASELINE] + [n for n in m2_names if n != BASELINE] + list(frozen["variantes"]) + [clf["nome"]]

    groups = standard_groups(ref_rows, "teste")
    metrics = {n: group_metrics(ref_rows, predicted[n], groups) for n in names}
    write_csv(out_dir / "metricas.csv", [{"config": n, **m} for n in names for m in metrics[n]])

    decisions = []
    for i, r in enumerate(ref_rows):
        entry = {"frame_id": r["frame_id"], "date": r["date"], "condition": r["condition"], "time": r["time"],
                 "space_id": r["space_id"], "label": r["label"]}
        for n in names:
            entry[f"pred_{n}"] = predicted[n][i]
        for n in specs:
            entry[f"score_{n}"] = rows[n][i]["score"]
        entry[f"prob_{clf['nome']}"] = float(probabilities[i])
        decisions.append(entry)
    write_csv(out_dir / "decisoes.csv", decisions)
    final_base = clf["base"] if final == clf["nome"] else final
    write_csv(out_dir / f"vagas_{final}.csv",
              [{**r, "predicted": p} for r, p in zip(rows[final_base], predicted[final])])

    # Contagem por quadro (saída que um painel de ocupação exibiria).
    per_frame = defaultdict(lambda: {n: 0 for n in names + ["label"]})
    frame_info = {}
    for i, r in enumerate(ref_rows):
        per_frame[r["frame_id"]]["label"] += r["label"]
        frame_info[r["frame_id"]] = (r["date"], r["condition"], r["time"])
        for n in names:
            per_frame[r["frame_id"]][n] += predicted[n][i]
    write_csv(out_dir / "contagem_por_quadro.csv",
              [{"frame_id": fid, "date": frame_info[fid][0], "condition": frame_info[fid][1], "time": frame_info[fid][2],
                "ocupadas_rotulo": c["label"], **{f"ocupadas_{n}": c[n] for n in names}} for fid, c in per_frame.items()])

    # Comparações (mesmas vagas-quadro, mesmas referências e mesmos rótulos).
    comparisons = [
        ("Baseline x final", "O sistema final da M3 supera o baseline da M2 em dias inéditos?", BASELINE, final),
        ("E3", "A referência adaptativa reduz os erros da deriva de iluminação ao longo do dia?", "fixa", "adaptativa"),
        ("E4", "Manter a referência fixa ao lado da adaptativa evita os travamentos da adaptativa?", "adaptativa", "dupla"),
        ("E5", "A regressão logística sobre vários descritores supera a regra de limiar único?", "dupla", clf["nome"]),
        ("E1 (reavaliação)", "A morfologia (M2) continua útil em dias inéditos?", "A_M2", BASELINE),
        ("E2 (reavaliação)", "A compensação global de ganho (M2) continua com efeito misto?", BASELINE, "C_M2"),
    ]
    total = {n: next(m for m in metrics[n] if m["group"] == "teste · total") for n in names}
    comp_rows = []
    for cid, question, base, variant in comparisons:
        fb = fixed_broken(ref_rows, predicted[base], predicted[variant])
        comp_rows.append({"id": cid, "pergunta": question, "base": base, "variante": variant,
                          "f1_base": total[base]["f1"], "f1_variante": total[variant]["f1"],
                          "fp_base": total[base]["fp"], "fp_variante": total[variant]["fp"],
                          "fn_base": total[base]["fn"], "fn_variante": total[variant]["fn"],
                          "ema_base": total[base]["count_mae"], "ema_variante": total[variant]["count_mae"],
                          "erros_corrigidos": fb["fixed"], "erros_introduzidos": fb["broken"]})
    write_csv(out_dir / "comparacoes.csv", comp_rows)

    # Critérios de sucesso definidos na M2, aplicados ao sistema final.
    crit = experiment["criterios_sucesso"]
    day_metrics = {m["group"].split("dia ")[1]: m for m in metrics[final] if " · dia " in m["group"]}
    rain = next((m for m in metrics[final] if m["group"] == "teste · condição Rainy"), None)
    criteria = [[f"F1 ≥ {fmt(crit['f1_min_por_dia'], 2)} em cada dia de teste", d, day_metrics[d]["f1"],
                 "sim" if day_metrics[d]["f1"] >= crit["f1_min_por_dia"] else "não"] for d in sorted(day_metrics)]
    if rain:
        criteria.append([f"Especificidade ≥ {fmt(crit['especificidade_min_chuva'], 2)} nos quadros de chuva", "chuva",
                         rain["specificity"], "sim" if rain["specificity"] >= crit["especificidade_min_chuva"] else "não"])
    criteria += [[f"EMA de contagem ≤ {fmt(crit['ema_contagem_max'], 1)} vaga por imagem", d, day_metrics[d]["count_mae"],
                  "sim" if day_metrics[d]["count_mae"] <= crit["ema_contagem_max"] else "não"] for d in sorted(day_metrics)]

    # ---- figuras
    timeline = []
    for d in days:
        fids = [fid for fid in per_frame if frame_info[fid][0] == d]
        fids.sort(key=lambda f: frame_info[f][2])
        entry = {"title": f"Teste · {d}", "times": [frame_info[f][2] for f in fids],
                 "true": [per_frame[f]["label"] for f in fids]}
        for n in (BASELINE, final):
            entry[n] = [per_frame[f][n] for f in fids]
        timeline.append(entry)
    viz.plot_counts(timeline, [BASELINE, final], out_dir / "fig_contagem_teste.png")

    hours = sorted({int(r["time"][:2]) for r in ref_rows})
    hourly = {}
    for n in (BASELINE, "adaptativa", final):
        fp = [sum(predicted[n][i] and not r["label"] for i, r in enumerate(ref_rows) if int(r["time"][:2]) == h) for h in hours]
        fn = [sum(r["label"] and not predicted[n][i] for i, r in enumerate(ref_rows) if int(r["time"][:2]) == h) for h in hours]
        hourly[n] = {"fp": fp, "fn": fn}
    viz.plot_errors_by_hour(hourly, hours, out_dir / "fig_erros_por_hora.png", "Erros por hora nos dias de teste")

    space_ids = sorted({r["space_id"] for r in ref_rows})
    for n in (BASELINE, final):
        fp = np.array([sum(predicted[n][i] and not r["label"] for i, r in enumerate(ref_rows) if r["space_id"] == s) for s in space_ids])
        fn = np.array([sum(r["label"] and not predicted[n][i] for i, r in enumerate(ref_rows) if r["space_id"] == s) for s in space_ids])
        viz.plot_errors_by_space(fp, fn, space_ids, f"Erros por vaga nos dias de teste · {n}", out_dir / f"fig_erros_por_vaga_{n}.png")

    # Casos de sucesso e falha do sistema final e pior quadro: reprocessa o dia até o quadro escolhido.
    score_final = np.array([r["score"] for r in rows[final_base]])
    rank = probabilities if final == clf["nome"] else score_final
    kinds = {"Sucesso (VP)": (1, 1), "Sucesso (VN)": (0, 0), "Falha (FP)": (0, 1), "Falha (FN)": (1, 0)}
    cases = []
    for kind, (label, pred) in kinds.items():
        idx = [i for i, r in enumerate(ref_rows) if r["label"] == label and predicted[final][i] == pred]
        if not idx:
            continue
        idx.sort(key=lambda i: rank[i])
        chosen = idx[-1] if kind == "Falha (FP)" else idx[0] if kind == "Falha (FN)" else idx[len(idx) // 2]
        cases.append((kind, chosen))
    errors_final = defaultdict(int)
    errors_base = defaultdict(int)
    for i, r in enumerate(ref_rows):
        errors_final[r["frame_id"]] += predicted[final][i] != r["label"]
        errors_base[r["frame_id"]] += predicted[BASELINE][i] != r["label"]
    worst_final = max(errors_final, key=lambda f: (errors_final[f], f))
    worst_base = max(errors_base, key=lambda f: (errors_base[f], f))
    wanted = {ref_rows[i]["frame_id"] for _, i in cases} | {worst_final, worst_base}
    snapshots = {fid: final_base for fid in wanted}
    run_sequences(data, "teste", {final_base: specs[final_base]}, compact=True, snapshots=snapshots)

    def regions_of(date: str) -> dict:
        return {r.id: r for r in data.reference(date, specs[final_base][0]).regions}

    case_grid = []
    for kind, i in cases:
        r = ref_rows[i]
        s = snapshots[r["frame_id"]]
        region = regions_of(r["date"])[r["space_id"]]
        box = crop_box(region, s["gray"].shape)
        steps = s["steps"]
        crops = [crop(s["fixed"], region, box), crop(s["adaptive"], region, box), crop(s["image"], region, box),
                 crop(viz.diff_view(steps["fix"]["diff"]), region, box), crop(steps["fix"]["closed"], region, box),
                 crop(viz.diff_view(steps["ad"]["diff"]), region, box), crop(steps["ad"]["closed"], region, box)]
        value = (f"p = {fmt(float(probabilities[i]), 2)}" if final == clf["nome"]
                 else f"escore {fmt(rows[final_base][i]['score'], 2)}")  # escore do sistema final, não do baseline
        case_grid.append({"title": f"{kind}\n{r['frame_id']}\nvaga {r['space_id']} · {value}", "crops": crops})
    viz.plot_case_grid(case_grid, ["Ref. fixa", "Ref. adaptativa", "Atual", "Dif. fixa", "Máscara fixa",
                                   "Dif. adaptativa", "Máscara adapt."], out_dir / f"fig_casos_{final}.png")

    for tag, fid in (("final", worst_final), ("baseline", worst_base)):
        s = snapshots[fid]
        labels = data.labels(next(f for f in data.frames["teste"] if f.id == fid))
        idx = [i for i, r in enumerate(ref_rows) if r["frame_id"] == fid]
        for n in (BASELINE, final):
            shown = [{"space_id": ref_rows[i]["space_id"], "predicted": predicted[n][i]} for i in idx]
            n_err = sum(predicted[n][i] != ref_rows[i]["label"] for i in idx)
            occupied = sum(predicted[n][i] for i in idx)
            overlay = viz.draw_result(s["image"], list(regions_of(fid[:10]).values()), shown, labels,
                                      [f"{n} | {fid}", f"Ocupadas: {occupied} (rotulo {sum(ref_rows[i]['label'] for i in idx)})"
                                       f" | erros: {n_err}"])
            cv2.imwrite(str(out_dir / f"fig_quadro_{tag}_{n}.jpg"), overlay, [cv2.IMWRITE_JPEG_QUALITY, 85])

    # ---- resumo em Markdown
    md = ["# Teste final da M3 (gerado por `src/run_final.py --etapa teste`)", ""]
    md += ["Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.", ""]
    md += [f"Parâmetros lidos de `models/sistema_final_m3.json` (gerado em {frozen['gerado_em']}, "
           f"commit do código {str(frozen['commit_do_codigo'])[:10]}). Sistema final: **{final}**.", ""]
    n_frames = len({r['frame_id'] for r in ref_rows})
    md += [f"Dias de teste: {', '.join(days)} — {n_frames} quadros, {len(ref_rows)} vaga-quadros rotulados.", ""]
    md += ["## Configurações avaliadas", ""]
    desc = {BASELINE: "Baseline: configuração B da M2 congelada (referência fixa, T = 25, τ = 0,24)",
            "A_M2": "Configuração A da M2 congelada (sem morfologia)",
            "C_M2": "Configuração C da M2 congelada (ganho global)",
            clf["nome"]: clf["descricao"]}
    desc.update({v: frozen["variantes"][v]["descricao"] for v in frozen["variantes"]})
    md.append(markdown_table(["Configuração", "Descrição", "Limiar"],
                             [[n, desc[n], fmt(taus[n] if n in taus else model.threshold, 2)] for n in names]))
    md += ["", "## Indicadores (total do teste)", ""]
    md.append(markdown_table(
        ["Configuração", "VP", "FP", "FN", "VN", "Acurácia", "Precisão", "Revocação", "Especificidade", "F1",
         "Acur. balanceada", "EMA contagem", "Viés contagem", "Erro máx."],
        [[n, total[n]["tp"], total[n]["fp"], total[n]["fn"], total[n]["tn"], total[n]["accuracy"], total[n]["precision"],
          total[n]["recall"], total[n]["specificity"], total[n]["f1"], total[n]["balanced_accuracy"],
          total[n]["count_mae"], total[n]["count_bias"], total[n]["count_max_abs"]] for n in names]))
    md += ["", "EMA contagem = erro médio absoluto do nº de vagas ocupadas por imagem; viés > 0 = superestima.", ""]
    md += ["## Indicadores por dia, segmento e condição", ""]
    md.append(markdown_table(
        ["Configuração", "Grupo", "n", "FP", "FN", "F1", "Especificidade", "Acur. balanceada", "EMA contagem"],
        [[n, m["group"], m["n"], m["fp"], m["fn"], m["f1"], m["specificity"], m["balanced_accuracy"], m["count_mae"]]
         for n in names for m in metrics[n] if m["group"] != "teste · total"]))
    md += ["", "## Comparações controladas (mesmas vagas-quadro, referências e rótulos)", ""]
    md.append(markdown_table(
        ["Id", "Pergunta", "Base → variante", "F1", "FP", "FN", "EMA", "Corrigidos", "Introduzidos"],
        [[c["id"], c["pergunta"], f"{c['base']} → {c['variante']}", f"{fmt(c['f1_base'])} → {fmt(c['f1_variante'])}",
          f"{c['fp_base']} → {c['fp_variante']}", f"{c['fn_base']} → {c['fn_variante']}",
          f"{fmt(c['ema_base'], 2)} → {fmt(c['ema_variante'], 2)}", c["erros_corrigidos"], c["erros_introduzidos"]]
         for c in comp_rows]))
    md += ["", f"## Critérios de sucesso (definidos na M2) aplicados ao sistema final ({final})", ""]
    md.append(markdown_table(["Critério", "Grupo", "Valor", "Atendido"], criteria))
    md += ["", "## Casos ilustrados", ""]
    md += [f"- {kind}: `{ref_rows[i]['frame_id']}`, vaga {ref_rows[i]['space_id']}." for kind, i in cases]
    md += [f"- Pior quadro do sistema final: `{worst_final}` ({errors_final[worst_final]} erros; "
           f"baseline no mesmo quadro: {errors_base[worst_final]}).",
           f"- Pior quadro do baseline: `{worst_base}` ({errors_base[worst_base]} erros; "
           f"sistema final no mesmo quadro: {errors_final[worst_base]}).", ""]
    (out_dir / "resultados.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Resultados em {(out_dir / 'resultados.md').relative_to(REPO_ROOT).as_posix()}")


def m2_name(name: str) -> str:
    """A_sem_morfologia -> A_M2 (nome curto usado nas tabelas da M3)."""
    return f"{name.split('_')[0]}_M2"


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação final da M3 (desenvolvimento e teste).")
    parser.add_argument("--etapa", choices=["desenvolvimento", "teste"], required=True)
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT), help="arquivo JSON do experimento")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1),
                        help="processos em paralelo na busca em grade e no teste (resultado não depende disso)")
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    data = Dataset(experiment)
    out_dir = resolve(experiment["results_dir"]) / args.etapa
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.etapa == "desenvolvimento":
        stage_development(experiment, data, out_dir, args.workers)
    else:
        stage_test(experiment, data, out_dir, args.workers)


if __name__ == "__main__":
    main()
