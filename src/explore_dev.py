"""Explorações no desenvolvimento que levaram a descartar duas ideias na M3.

    python src/explore_dev.py

Usa só os dias de desenvolvimento (os de teste nem são listados) e os parâmetros congelados
em `models/sistema_final_m3.json`. As explorações originais foram feitas antes do
congelamento, com parâmetros provisórios e scripts não versionados; este script as refaz
com o código do repositório para que a evidência seja rastreável. Nada aqui altera o
sistema final nem os parâmetros congelados.

X1 — Ganho estimado nas vagas livres (sugestão da M2, item M3-2a). Antes de comparar cada
quadro, a referência adaptativa é multiplicada por g = mediana(quadro) / mediana(referência),
as duas medianas tomadas só nos pixels das vagas julgadas livres no quadro anterior.
Comparado com as variantes adaptativa e dupla sem o ganho (mesmos alpha, free_max e tau).

X2 — Textura sem referência, como no artigo do PKLot (Almeida et al., 2015). Regressão
logística com validação cruzada deixando um dia de fora (o mesmo procedimento da dupla_LR),
sobre três conjuntos de descritores:
- textura: histograma LBP uniforme invariante à rotação (8 vizinhos, raio 1; 10 classes),
  desvio padrão do cinza, densidade de bordas e croma médio do quadro atual (sem referência);
- diferença: os 7 descritores da dupla_LR (contra as referências fixa e adaptativa);
- os dois juntos.

Saídas em `images/results/m3/exploracao/`.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import cv2
import numpy as np

from parking.classifier import LogisticModel
from parking.experiment import load_experiment, read_image, resolve, write_csv
from parking.metrics import classification_metrics
from parking.pipeline import PipelineConfig, analyze, preprocess
from parking.sequence import DayProcessor, SequenceConfig
from run_final import DEFAULT_EXPERIMENT, FROZEN, Dataset, fmt, group_metrics, markdown_table, standard_groups, taus_from, tune_threshold

LBP_BINS = 10  # 0..8 = padrões uniformes pelo nº de vizinhos >= centro; 9 = não uniformes
TEXTURE = [f"lbp{i}" for i in range(LBP_BINS)] + ["gray_std", "edge_density", "croma_atual"]


class GainDayProcessor(DayProcessor):
    """DayProcessor com ganho global na referência adaptativa, estimado nas vagas livres do quadro anterior."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_free = []
        self.gains: list[float] = []

    def step(self, gray, keep_steps=False, fixed_result=None):
        if self.previous_free:
            current = np.concatenate([gray[y : y + h, x : x + w][r.mask]
                                      for r in self.previous_free for x, y, w, h in [r.bbox]])
            reference = np.concatenate([self.adaptive[y : y + h, x : x + w][r.mask]
                                        for r in self.previous_free for x, y, w, h in [r.bbox]])
            gain = float(np.median(current)) / max(float(np.median(reference)), 1.0)
            self.adaptive = np.clip(self.adaptive * gain, 0, 255).astype(np.float32)
            self.gains.append(gain)
        rows, steps = super().step(gray, keep_steps, fixed_result)
        self.previous_free = [r for r, row in zip(self.fixed.regions, rows) if row["score"] < self.seq.free_max]
        return rows, steps


def lbp_riu2(gray: np.ndarray) -> np.ndarray:
    """Código LBP uniforme invariante à rotação (P = 8, R = 1) de cada pixel; 255 na borda."""
    g = gray.astype(np.int16)
    center = g[1:-1, 1:-1]
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]  # em círculo
    bits = np.stack([g[1 + dy : g.shape[0] - 1 + dy, 1 + dx : g.shape[1] - 1 + dx] >= center
                     for dy, dx in offsets]).astype(np.uint8)
    transitions = (bits != np.roll(bits, 1, axis=0)).sum(0)
    code = np.where(transitions <= 2, bits.sum(0), LBP_BINS - 1).astype(np.uint8)
    return np.pad(code, 1, constant_values=255)


def texture_features(image: np.ndarray, regions) -> dict[int, dict]:
    codes = lbp_riu2(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.sqrt((lab[..., 1] - 128) ** 2 + (lab[..., 2] - 128) ** 2)
    out = {}
    for region in regions:
        x, y, w, h = region.bbox
        c = codes[y : y + h, x : x + w][region.mask]
        c = c[c != 255]
        hist = np.bincount(c, minlength=LBP_BINS)[:LBP_BINS] / max(c.size, 1)
        out[region.id] = {**{f"lbp{i}": float(hist[i]) for i in range(LBP_BINS)},
                          "croma_atual": float(chroma[y : y + h, x : x + w][region.mask].mean())}
    return out


def cross_validate(rows: list[dict], features: list[str], lam: float, taus: np.ndarray, days: list[str]) -> list[dict]:
    """Ajusta em dois dias e avalia no terceiro; limiar de probabilidade pelo maior F1 no treino."""
    out, pooled_labels, pooled_preds = [], [], []
    for held in days:
        train = [r for r in rows if r["date"] != held]
        test = [r for r in rows if r["date"] == held]
        model = LogisticModel.fit(train, features, lam)
        model.threshold = tune_threshold(model.proba(train), [r["label"] for r in train], taus)["tau"]
        labels, preds = [r["label"] for r in test], model.predict(test).tolist()
        out.append({"dia_avaliado": held, "limiar": model.threshold, **classification_metrics(labels, preds)})
        pooled_labels += labels
        pooled_preds += preds
    out.append({"dia_avaliado": "todos (agregado)", "limiar": None, **classification_metrics(pooled_labels, pooled_preds)})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Explorações da M3 no desenvolvimento (ganho e textura).")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT))
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    with open(FROZEN, encoding="utf-8") as f:
        frozen = json.load(f)
    data = Dataset(experiment, ["desenvolvimento"])
    days = data.days("desenvolvimento")
    cfg = PipelineConfig.from_dict(frozen["pipeline"])
    seqs = {v: SequenceConfig.from_dict(frozen["variantes"][v]) for v in ("adaptativa", "dupla")}
    taus = {"adaptativa": frozen["variantes"]["adaptativa"]["tau"], "dupla": frozen["variantes"]["dupla"]["tau"]}
    taus["adaptativa + ganho"], taus["dupla + ganho"] = taus["adaptativa"], taus["dupla"]
    out_dir = resolve(experiment["results_dir"]) / "exploracao"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = defaultdict(list)
    gains = {}
    print(f"Explorações: {len(days)} dias de desenvolvimento ...", flush=True)
    for date in days:
        reference = data.reference(date, cfg)
        procs = {"adaptativa": DayProcessor(reference, cfg, seqs["adaptativa"]),
                 "adaptativa + ganho": GainDayProcessor(reference, cfg, seqs["adaptativa"]),
                 "dupla": DayProcessor(reference, cfg, seqs["dupla"]),
                 "dupla + ganho": GainDayProcessor(reference, cfg, seqs["dupla"])}
        for frame in data.day_frames("desenvolvimento", date):
            image = read_image(frame.path)
            gray = preprocess(image, cfg)
            fixed = analyze(gray, reference, cfg)
            labels = data.labels(frame)
            texture = texture_features(image, reference.regions)
            for name, proc in procs.items():
                out, _ = proc.step(gray, fixed_result=fixed if proc.seq.use_fixed else None)
                for r in out:
                    if labels.get(r["space_id"]) is None:
                        continue
                    row = {"frame_id": frame.id, "date": frame.date, "condition": frame.condition, "time": frame.time,
                           **r, "label": labels[r["space_id"]]}
                    if name == "dupla":
                        row.update(texture[r["space_id"]])
                    rows[name].append(row)
        for name in ("adaptativa + ganho", "dupla + ganho"):
            g = procs[name].gains
            gains[(date, name)] = (min(g), float(np.median(g)), max(g))

    # X1: ganho nas vagas livres
    x1 = []
    for name in ("adaptativa", "adaptativa + ganho", "dupla", "dupla + ganho"):
        preds = [int(r["score"] >= taus[name]) for r in rows[name]]
        x1 += [{"variante": name, "tau": taus[name], **m}
               for m in group_metrics(rows[name], preds, standard_groups(rows[name], "dev"))]
    write_csv(out_dir / "exploracao_ganho.csv", x1)

    # X2: textura sem referência x diferença, regressão logística com validação por dia
    clf = frozen["classificador"]
    sets = {"textura (sem referência)": TEXTURE, "diferença (descritores da dupla_LR)": clf["features"],
            "textura + diferença": TEXTURE + clf["features"]}
    grid = taus_from(experiment["busca"]["tau"])
    x2 = []
    for name, feats in sets.items():
        x2 += [{"descritores": name, **m} for m in cross_validate(rows["dupla"], feats, clf["lam"], grid, days)]
    write_csv(out_dir / "exploracao_textura.csv", x2)

    md = ["# Explorações no desenvolvimento (gerado por `src/explore_dev.py`)", ""]
    md += ["Arquivo gerado automaticamente; não edite à mão. Só dias de desenvolvimento; parâmetros de "
           "`models/sistema_final_m3.json`. Classe positiva = vaga ocupada.", ""]
    md += ["## X1 — Ganho estimado nas vagas livres", ""]
    md.append(markdown_table(
        ["Variante", "Grupo", "n", "FP", "FN", "F1", "Especificidade", "EMA contagem"],
        [[m["variante"], m["group"], m["n"], m["fp"], m["fn"], m["f1"], m["specificity"], m["count_mae"]] for m in x1]))
    md += ["", "Ganho aplicado à referência adaptativa (mínimo, mediana e máximo por dia):", ""]
    md.append(markdown_table(["Dia", "Variante", "Mínimo", "Mediana", "Máximo"],
                             [[d, n, g[0], g[1], g[2]] for (d, n), g in sorted(gains.items())]))
    md += ["", "## X2 — Textura sem referência (LBP) x diferença, regressão logística", ""]
    md += [f"Validação cruzada deixando um dia de fora; λ = {fmt(clf['lam'], 1)}; limiar de probabilidade "
           "pelo maior F1 nos dois dias de treino. Descritores de textura: " + ", ".join(f"`{t}`" for t in TEXTURE) + ".", ""]
    md.append(markdown_table(
        ["Descritores", "Dia avaliado", "Limiar", "VP", "FP", "FN", "VN", "F1", "Especificidade"],
        [[m["descritores"], m["dia_avaliado"], "—" if m["limiar"] is None else fmt(m["limiar"], 2), m["tp"], m["fp"],
          m["fn"], m["tn"], m["f1"], m["specificity"]] for m in x2]))
    md.append("")
    (out_dir / "resultados_exploracao.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Resultados em {(out_dir / 'resultados_exploracao.md').relative_to(resolve('.')).as_posix()}")


if __name__ == "__main__":
    main()
