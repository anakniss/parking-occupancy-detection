"""Ajusta os limiares no dia de ajuste, avalia nos dias de teste e compara as configurações.

Exemplo (a partir da raiz do repositório):
    python src/run_experiments.py

Protocolo (definido em configs/experimento_m2.json):
- uma referência (estacionamento livre) por dia, excluída da avaliação;
- T (limiar da diferença) e τ (limiar de ocupação) são escolhidos SOMENTE no dia de
  ajuste, maximizando o F1; em empate, vence o T com a faixa de τ ótimos mais larga,
  e τ é a mediana dessa faixa;
- os dias de teste são avaliados uma única vez com os parâmetros congelados.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, replace

import cv2
import numpy as np

from parking import visualize as viz
from parking.dataset import Frame, list_frames, load_spaces
from parking.experiment import (
    DEFAULT_EXPERIMENT,
    REPO_ROOT,
    config_from,
    load_experiment,
    load_reference,
    read_image,
    resolve,
    write_csv,
)
from parking.metrics import auc, classification_metrics, count_metrics, sweep_f1
from parking.pipeline import PipelineConfig, Reference, analyze, preprocess

DESCRIPTORS = {
    "largest_frac": "fração da vaga no maior componente (adim.)",
    "frac_changed": "fração da vaga marcada como alterada (adim.)",
    "mean_diff": "média da diferença absoluta na vaga (níveis de cinza)",
    "n_components": "nº de componentes >= área mínima",
    "largest_solidity": "solidez do maior componente (adim.)",
    "edge_density": "densidade de bordas de Canny no quadro atual (adim.)",
    "gray_std": "desvio padrão do cinza no quadro atual (níveis de cinza)",
}


class Data:
    """Quadros, rótulos e referências, com cache das imagens pré-processadas."""

    def __init__(self, experiment: dict):
        self.experiment = experiment
        self.frames = list_frames(resolve(experiment["dataset_root"]))
        self.reference_paths = {date: resolve(p) for date, p in experiment["references"].items()}
        self.reference_ids = {p.stem for p in self.reference_paths.values()}
        self.labels = {f.id: {s.id: s.occupied for s in load_spaces(f.xml_path)} for f in self.frames}
        self.conditions = {f.date: f.condition for f in self.frames}
        self._gray: dict = {}
        self._references: dict = {}

    def split(self, frame: Frame) -> str:
        if frame.id in self.reference_ids:
            return "referencia"
        if frame.date in self.experiment["tuning_dates"]:
            return "ajuste"
        if frame.date in self.experiment["test_dates"]:
            return "teste"
        return "nao_usado"

    def frames_of(self, split: str) -> list[Frame]:
        return [f for f in self.frames if self.split(f) == split]

    def gray(self, frame: Frame, cfg: PipelineConfig) -> np.ndarray:
        key = (frame.id, cfg.blur_ksize)
        if key not in self._gray:
            self._gray[key] = preprocess(read_image(frame.path), cfg)
        return self._gray[key]

    def reference(self, date: str, cfg: PipelineConfig) -> Reference:
        key = (date, cfg.blur_ksize)
        if key not in self._references:
            self._references[key] = load_reference(self.reference_paths[date], cfg)
        return self._references[key]

    def day_title(self, date: str) -> str:
        return f"{date} ({self.conditions[date]})"


def evaluate(data: Data, frames: list[Frame], cfg: PipelineConfig) -> list[dict]:
    rows = []
    for frame in frames:
        result = analyze(data.gray(frame, cfg), data.reference(frame.date, cfg), cfg)
        for row in result.rows:
            rows.append(
                {
                    "frame_id": frame.id,
                    "date": frame.date,
                    "condition": frame.condition,
                    "time": frame.time,
                    "split": data.split(frame),
                    "gain": result.gain,
                    **row,
                    "label": data.labels[frame.id][row["space_id"]],
                }
            )
    return [r for r in rows if r["label"] is not None]


def tune(data: Data, cfg: PipelineConfig, search: dict) -> tuple[PipelineConfig, list[dict]]:
    """Busca em grade de T e τ no dia de ajuste (critério: F1)."""
    spec = search["occupancy_threshold"]
    taus = np.round(np.arange(spec["start"], spec["stop"] + 1e-9, spec["step"]), 4)
    frames = data.frames_of("ajuste")
    curve = []
    for threshold in search["diff_threshold"]:
        rows = evaluate(data, frames, replace(cfg, diff_threshold=threshold))
        scores = [r["largest_frac"] for r in rows]
        labels = [r["label"] for r in rows]
        f1 = sweep_f1(scores, labels, taus)
        best = f1.max()
        plateau = taus[np.isclose(f1, best)]
        curve.append(
            {
                "diff_threshold": threshold,
                "best_f1": float(best),
                "tau_min": float(plateau.min()),
                "tau_max": float(plateau.max()),
                "tau_selected": float(np.round(np.median(plateau), 2)),
                "n_optimal_taus": int(plateau.size),
            }
        )
    chosen = max(curve, key=lambda c: (round(c["best_f1"], 6), c["n_optimal_taus"]))
    tuned = replace(cfg, diff_threshold=chosen["diff_threshold"], occupancy_threshold=chosen["tau_selected"])
    return tuned, curve


def metrics_by_group(data: Data, rows: list[dict]) -> list[dict]:
    groups = [(f"ajuste · {data.day_title(d)}", lambda r, d=d: r["date"] == d) for d in data.experiment["tuning_dates"]]
    groups += [(f"teste · {data.day_title(d)}", lambda r, d=d: r["date"] == d) for d in data.experiment["test_dates"]]
    groups += [("teste · total", lambda r: r["split"] == "teste")]
    out = []
    for name, keep in groups:
        selected = [r for r in rows if keep(r)]
        per_frame = defaultdict(lambda: [0, 0, 0])
        for r in selected:
            per_frame[r["frame_id"]][0] += r["label"]
            per_frame[r["frame_id"]][1] += r["predicted"]
            per_frame[r["frame_id"]][2] += 1
        counts = np.array(list(per_frame.values()))
        out.append(
            {
                "group": name,
                **classification_metrics([r["label"] for r in selected], [r["predicted"] for r in selected]),
                **count_metrics(counts[:, 0], counts[:, 1], int(counts[0, 2])),
            }
        )
    return out


def compare(baseline: list[dict], variant: list[dict]) -> dict:
    """Erros corrigidos/introduzidos pela variante (pares vaga-quadro do teste)."""
    key = lambda r: (r["frame_id"], r["space_id"])  # noqa: E731
    base = {key(r): r for r in baseline if r["split"] == "teste"}
    fixed = broken = 0
    for r in variant:
        if r["split"] != "teste":
            continue
        b = base[key(r)]
        base_ok, var_ok = b["predicted"] == b["label"], r["predicted"] == r["label"]
        fixed += (not base_ok) and var_ok
        broken += base_ok and not var_ok
    return {"fixed": int(fixed), "broken": int(broken)}


def noise_stats(rows: list[dict]) -> dict:
    test = [r for r in rows if r["split"] == "teste"]
    free = [r for r in test if r["label"] == 0]
    occupied = [r for r in test if r["label"] == 1]
    return {
        "components_free_mean": float(np.mean([r["n_components"] for r in free])),
        "largest_frac_free_median": float(np.median([r["largest_frac"] for r in free])),
        "largest_frac_occupied_median": float(np.median([r["largest_frac"] for r in occupied])),
    }


def pick_cases(rows: list[dict]) -> list[tuple[str, dict]]:
    """Um sucesso de cada classe (valor mediano) e o pior erro de cada tipo, no teste."""
    test = [r for r in rows if r["split"] == "teste"]
    groups = {
        "Sucesso (VP)": [r for r in test if r["label"] == 1 and r["predicted"] == 1],
        "Sucesso (VN)": [r for r in test if r["label"] == 0 and r["predicted"] == 0],
        "Falha (FP)": [r for r in test if r["label"] == 0 and r["predicted"] == 1],
        "Falha (FN)": [r for r in test if r["label"] == 1 and r["predicted"] == 0],
    }
    cases = []
    for kind, items in groups.items():
        if not items:
            continue
        items = sorted(items, key=lambda r: r["largest_frac"])
        if kind == "Falha (FP)":
            chosen = items[-1]
        elif kind == "Falha (FN)":
            chosen = items[0]
        else:
            chosen = items[len(items) // 2]
        cases.append((kind, chosen))
    return cases


def case_crops(data: Data, cfg: PipelineConfig, row: dict, margin: int = 14) -> dict:
    frame = next(f for f in data.frames if f.id == row["frame_id"])
    reference = data.reference(frame.date, cfg)
    result = analyze(data.gray(frame, cfg), reference, cfg, keep_steps=True)
    steps = result.steps
    region = next(r for r in reference.regions if r.id == row["space_id"])
    x, y, w, h = region.bbox
    height, width = reference.gray.shape
    x0, y0, x1, y1 = max(x - margin, 0), max(y - margin, 0), min(x + w + margin, width), min(y + h + margin, height)

    def crop(img: np.ndarray) -> np.ndarray:
        out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img.copy()
        cv2.polylines(out, [region.contour], True, (214, 120, 42), 1, cv2.LINE_AA)
        return out[y0:y1, x0:x1]

    # apenas os componentes desta vaga (os das vagas vizinhas ficam de fora)
    own = np.zeros_like(reference.gray)
    inside = own[y : y + h, x : x + w]
    inside[region.mask & (steps["components"][y : y + h, x : x + w] > 0)] = 255

    return {
        "reference": crop(reference.gray),
        "current": crop(steps["compared"]),
        "diff": crop(viz.diff_view(steps["diff"])),
        "binary": crop(steps["binary"]),
        "closed": crop(steps["closed"]),
        "components": crop(own),
    }


def fmt(value, digits: int = 3) -> str:
    if isinstance(value, float):
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")
    return str(value)


def markdown_table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimentos da M2 (ajuste, teste e comparações).")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT), help="arquivo JSON do experimento")
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    out_dir = resolve(experiment["results_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    data = Data(experiment)
    names = list(experiment["configs"])

    # ---- manifesto dos dados
    manifest = [
        {
            "frame_id": f.id,
            "condition": f.condition,
            "date": f.date,
            "time": f.time,
            "split": data.split(f),
            "spaces": len(data.labels[f.id]),
            "occupied": sum(v == 1 for v in data.labels[f.id].values()),
            "path": f.path.relative_to(REPO_ROOT).as_posix(),
        }
        for f in data.frames
    ]
    write_csv(out_dir / "manifesto_imagens.csv", manifest)

    # ---- ajuste, avaliação e métricas
    tuned, curves, rows, metrics = {}, {}, {}, {}
    for name in names:
        print(f"[{name}] ajustando T e tau no dia de ajuste...", flush=True)
        tuned[name], curves[name] = tune(data, config_from(experiment, name), experiment["search"])
        print(f"[{name}] T = {tuned[name].diff_threshold}, tau = {tuned[name].occupancy_threshold:.2f}; avaliando...")
        rows[name] = evaluate(data, data.frames_of("ajuste") + data.frames_of("teste"), tuned[name])
        metrics[name] = metrics_by_group(data, rows[name])
        write_csv(out_dir / f"ajuste_{name}.csv", curves[name])
        write_csv(out_dir / f"vagas_{name}.csv", rows[name])

    with open(out_dir / "parametros_ajustados.json", "w", encoding="utf-8") as f:
        json.dump({n: asdict(c) for n, c in tuned.items()}, f, indent=2, ensure_ascii=False)
    write_csv(out_dir / "metricas.csv", [{"config": n, **m} for n in names for m in metrics[n]])
    for name in names:
        file_cfg = config_from(experiment, name)
        if (file_cfg.diff_threshold, file_cfg.occupancy_threshold) != (
            tuned[name].diff_threshold,
            tuned[name].occupancy_threshold,
        ):
            print(
                f"AVISO: {name} no JSON usa T = {file_cfg.diff_threshold}, tau = {file_cfg.occupancy_threshold}; "
                f"o ajuste encontrou T = {tuned[name].diff_threshold}, tau = {tuned[name].occupancy_threshold}. "
                "Atualize o JSON para que run_pipeline.py use os valores ajustados."
            )

    comparisons = []
    for comp in experiment["comparisons"]:
        b, v = comp["baseline"], comp["variant"]
        comparisons.append(
            {**comp, **compare(rows[b], rows[v]), "noise_baseline": noise_stats(rows[b]), "noise_variant": noise_stats(rows[v])}
        )

    main_name = experiment["default_config"]
    separability = []
    for descriptor, description in DESCRIPTORS.items():
        entry = {"descriptor": descriptor, "description": description}
        for split in ("ajuste", "teste"):
            sel = [r for r in rows[main_name] if r["split"] == split]
            entry[f"auc_{split}"] = auc([r[descriptor] for r in sel], [r["label"] for r in sel])
        separability.append(entry)
    write_csv(out_dir / "separabilidade_descritores.csv", separability)

    # ---- figuras
    viz.plot_tuning(
        {n: ([c["diff_threshold"] for c in curves[n]], [c["best_f1"] for c in curves[n]]) for n in names},
        {n: tuned[n].diff_threshold for n in names},
        out_dir / "fig_ajuste_limiar.png",
    )

    days = []
    for date in experiment["tuning_dates"] + experiment["test_dates"]:
        frame_ids = [f.id for f in data.frames if f.date == date and data.split(f) != "referencia"]
        day = {
            "title": ("Ajuste · " if date in experiment["tuning_dates"] else "Teste · ") + data.day_title(date),
            "times": [f.time for f in data.frames if f.id in frame_ids],
            "true": [sum(v == 1 for v in data.labels[i].values()) for i in frame_ids],
        }
        for name in names:
            predicted = defaultdict(int)
            for r in rows[name]:
                predicted[r["frame_id"]] += r["predicted"]
            day[name] = [predicted[i] for i in frame_ids]
        days.append(day)
    viz.plot_counts(days, names, out_dir / "fig_contagem_temporal.png")

    space_ids = sorted({r["space_id"] for r in rows[main_name]})
    worst_frames = {}
    for name in names:
        panels = []
        for date in experiment["tuning_dates"] + experiment["test_dates"]:
            sel = [r for r in rows[name] if r["date"] == date]
            prefix = "Ajuste" if date in experiment["tuning_dates"] else "Teste"
            panels.append(
                {
                    "title": f"{prefix} · {data.day_title(date)}",
                    "scores": [r["largest_frac"] for r in sel],
                    "labels": [r["label"] for r in sel],
                    "tau": tuned[name].occupancy_threshold,
                }
            )
        viz.plot_score_histograms(panels, out_dir / f"fig_distribuicao_{name}.png")

        test = [r for r in rows[name] if r["split"] == "teste"]
        fp = np.array([sum(r["predicted"] and not r["label"] for r in test if r["space_id"] == s) for s in space_ids])
        fn = np.array([sum(r["label"] and not r["predicted"] for r in test if r["space_id"] == s) for s in space_ids])
        viz.plot_errors_by_space(fp, fn, space_ids, f"Erros por vaga nos dias de teste · {name}", out_dir / f"fig_erros_por_vaga_{name}.png")

        cases = pick_cases(rows[name])
        viz.plot_cases(
            [
                {
                    "title": f"{kind}\n{r['frame_id']}\nvaga {r['space_id']} · fração {fmt(r['largest_frac'], 2)}",
                    "crops": case_crops(data, tuned[name], r),
                }
                for kind, r in cases
            ],
            out_dir / f"fig_casos_{name}.png",
        )

        errors = defaultdict(int)
        for r in test:
            errors[r["frame_id"]] += r["predicted"] != r["label"]
        worst_id = max(errors, key=errors.get)
        worst_frames[name] = (worst_id, errors[worst_id], [(k, r["frame_id"], r["space_id"]) for k, r in cases])
        frame = next(f for f in data.frames if f.id == worst_id)
        reference = data.reference(frame.date, tuned[name])
        result = analyze(data.gray(frame, tuned[name]), reference, tuned[name])
        overlay = viz.draw_result(
            read_image(frame.path),
            reference.regions,
            result.rows,
            data.labels[worst_id],
            [f"{name} | {worst_id}", f"Erros: {errors[worst_id]} de {len(result.rows)} vagas"],
        )
        cv2.imwrite(str(out_dir / f"fig_pior_quadro_{name}.jpg"), overlay, [cv2.IMWRITE_JPEG_QUALITY, 88])

    # ---- resumo em Markdown
    md = ["# Resultados gerados por `src/run_experiments.py`", ""]
    md += ["Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.", ""]
    md += ["## Parâmetros ajustados (dia de ajuste)", ""]
    md.append(
        markdown_table(
            ["Configuração", "Descrição", "T", "τ", "F1 no ajuste", "faixa de τ ótimos"],
            [
                [
                    n,
                    experiment["configs"][n]["description"],
                    tuned[n].diff_threshold,
                    fmt(tuned[n].occupancy_threshold, 2),
                    max(c["best_f1"] for c in curves[n]),
                    f"{fmt(next(c for c in curves[n] if c['diff_threshold'] == tuned[n].diff_threshold)['tau_min'], 2)}"
                    f" – {fmt(next(c for c in curves[n] if c['diff_threshold'] == tuned[n].diff_threshold)['tau_max'], 2)}",
                ]
                for n in names
            ],
        )
    )
    md += ["", "## Indicadores por configuração e grupo de imagens", ""]
    md.append(
        markdown_table(
            ["Configuração", "Grupo", "n", "VP", "FP", "FN", "VN", "Acurácia", "Precisão", "Revocação",
             "Especificidade", "F1", "Acur. balanceada", "EMA contagem", "Viés contagem", "Erro máx."],
            [
                [n, m["group"], m["n"], m["tp"], m["fp"], m["fn"], m["tn"], m["accuracy"], m["precision"], m["recall"],
                 m["specificity"], m["f1"], m["balanced_accuracy"], m["count_mae"], m["count_bias"], m["count_max_abs"]]
                for n in names
                for m in metrics[n]
            ],
        )
    )
    md += ["", "EMA contagem = erro médio absoluto do nº de vagas ocupadas por imagem; viés > 0 = superestima.", ""]
    md += ["## Comparações controladas (dias de teste)", ""]
    md.append(
        markdown_table(
            ["Id", "Pergunta", "Base → Variante", "Erros corrigidos", "Erros introduzidos",
             "Comp. por vaga livre (base → var.)", "Mediana fração livre (base → var.)", "Mediana fração ocupada (base → var.)"],
            [
                [
                    c["id"],
                    c["question"],
                    f"{c['baseline']} → {c['variant']}",
                    c["fixed"],
                    c["broken"],
                    f"{fmt(c['noise_baseline']['components_free_mean'], 2)} → {fmt(c['noise_variant']['components_free_mean'], 2)}",
                    f"{fmt(c['noise_baseline']['largest_frac_free_median'], 3)} → {fmt(c['noise_variant']['largest_frac_free_median'], 3)}",
                    f"{fmt(c['noise_baseline']['largest_frac_occupied_median'], 3)} → {fmt(c['noise_variant']['largest_frac_occupied_median'], 3)}",
                ]
                for c in comparisons
            ],
        )
    )
    md += ["", f"## Separabilidade dos descritores ({main_name}, AUC ROC)", ""]
    md.append(
        markdown_table(
            ["Descritor", "Definição / unidade", "AUC ajuste", "AUC teste"],
            [[s["descriptor"], s["description"], fmt(s["auc_ajuste"], 4), fmt(s["auc_teste"], 4)] for s in separability],
        )
    )
    md += ["", "AUC = 0,5 não separa; 1,0 separa perfeitamente (valores < 0,5: o descritor é maior nas vagas livres).", ""]
    md += ["## Casos ilustrados e pior quadro do teste", ""]
    for name in names:
        worst_id, n_err, cases = worst_frames[name]
        listed = "; ".join(f"{k}: {fid} vaga {sid}" for k, fid, sid in cases)
        md.append(f"- **{name}** — pior quadro: `{worst_id}` ({n_err} erros). Casos: {listed}.")
    md.append("")
    (out_dir / "resultados.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Resultados em {out_dir.relative_to(REPO_ROOT).as_posix()}/resultados.md")


if __name__ == "__main__":
    main()
