"""Indicadores do teste por condição climática, a partir das decisões já registradas.

    python src/summarize_conditions.py

Não executa o pipeline nem altera parâmetros: lê `images/results/m3/teste/decisoes.csv`, gravado
uma única vez pela etapa de teste (`run_final.py --etapa teste`, parâmetros congelados), e reagrupa
as decisões por condição do PKLot (Sunny = sol, Cloudy = nublado, Rainy = chuva). Antes de gravar,
confere que os totais reproduzem `metricas.csv` (mesmos VP, FP, FN e VN por condição).

Taxa de falsa ocupada = FP / (FP + VN): fração das vagas livres que o sistema marca como ocupadas.
Taxa de falsa livre = FN / (FN + VP): fração das vagas ocupadas que o sistema marca como livres.

Saídas em `images/results/m3/teste/`: `por_condicao.csv` e `resultados_por_condicao.md`, com
- os indicadores de todas as configurações por condição;
- o experimento recomendado no parecer (diferença simples × diferença com compensação de ganho,
  `B_M2` × `C_M2`, sem reajuste) e a comparação baseline × final, separados por condição.
"""
from __future__ import annotations

import csv
from collections import defaultdict

import numpy as np

from parking.experiment import REPO_ROOT, write_csv
from parking.metrics import classification_metrics, count_metrics

TEST = REPO_ROOT / "images" / "results" / "m3" / "teste"
CONFIGS = ["B_M2", "A_M2", "C_M2", "fixa", "adaptativa", "dupla", "dupla_LR"]
CONDITIONS = [("Sunny", "sol"), ("Cloudy", "nublado"), ("Rainy", "chuva"), (None, "total")]
PAIRS = [
    ("E2 — diferença simples × compensação de ganho", "B_M2", "C_M2"),
    ("Baseline × final", "B_M2", "dupla"),
]


def fmt(value, digits: int = 3) -> str:
    if isinstance(value, float):
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")
    return str(value)


def metrics_for(rows: list[dict], config: str) -> dict:
    y_true = [int(r["label"]) for r in rows]
    y_pred = [int(r[f"pred_{config}"]) for r in rows]
    per_frame = defaultdict(lambda: [0, 0])
    for r, p in zip(rows, y_pred):
        per_frame[r["frame_id"]][0] += int(r["label"])
        per_frame[r["frame_id"]][1] += p
    counts = np.array(list(per_frame.values()))
    m = classification_metrics(y_true, y_pred)
    c = count_metrics(counts[:, 0], counts[:, 1], 40)
    return {
        **m,
        "false_occupied_rate": m["fp"] / (m["fp"] + m["tn"]) if m["fp"] + m["tn"] else float("nan"),
        "false_free_rate": m["fn"] / (m["fn"] + m["tp"]) if m["fn"] + m["tp"] else float("nan"),
        "frames": c["frames"],
        "count_mae": c["count_mae"],
        "count_bias": c["count_bias"],
        "count_max_abs": c["count_max_abs"],
    }


def check_against_metricas(table: list[dict]) -> None:
    with open(TEST / "metricas.csv", encoding="utf-8") as f:
        official = {(r["config"], r["group"]): r for r in csv.DictReader(f)}
    for row in table:
        group = "teste · total" if row["condition"] == "total" else f"teste · condição {row['condition_pklot']}"
        ref = official[(row["config"], group)]
        for key in ("tp", "fp", "fn", "tn"):
            if int(ref[key]) != row[key]:
                raise SystemExit(f"Divergência com metricas.csv em {row['config']} / {group} / {key}")


def main() -> None:
    with open(TEST / "decisoes.csv", encoding="utf-8") as f:
        decisions = list(csv.DictReader(f))

    table = []
    for config in CONFIGS:
        for pklot, name in CONDITIONS:
            rows = [r for r in decisions if pklot is None or r["condition"] == pklot]
            table.append({"config": config, "condition": name, "condition_pklot": pklot or "", "n": len(rows),
                          **{k: v for k, v in metrics_for(rows, config).items() if k != "n"}})
    check_against_metricas(table)
    write_csv(TEST / "por_condicao.csv", table)

    lines = [
        "# Teste final por condição climática (gerado por `src/summarize_conditions.py`)",
        "",
        "Arquivo gerado automaticamente; não edite à mão. Reagrupa as decisões congeladas de `decisoes.csv` "
        "(nenhum reajuste; os totais conferem com `metricas.csv`). Classe positiva = vaga ocupada. "
        "Taxa de falsa ocupada = FP / (FP + VN); taxa de falsa livre = FN / (FN + VP); "
        "EMA = erro médio absoluto do nº de vagas ocupadas por imagem.",
        "",
        "Condição = rótulo do PKLot para o quadro. Os 576 quadros do teste dividem-se em "
        + ", ".join(f"{name} {next(r['frames'] for r in table if r['condition'] == name)}" for _, name in CONDITIONS[:3])
        + ".",
        "",
        "## Todas as configurações",
        "",
        "| Configuração | Condição | Vaga-quadros | Livres | VP | FP | FN | VN | F1 | Especificidade | "
        "Taxa falsa ocupada | Taxa falsa livre | EMA contagem |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table:
        lines.append(
            f"| {r['config']} | {r['condition']} | {r['n']} | {r['fp'] + r['tn']} | {r['tp']} | {r['fp']} | "
            f"{r['fn']} | {r['tn']} | {fmt(r['f1'])} | {fmt(r['specificity'])} | {fmt(r['false_occupied_rate'])} | "
            f"{fmt(r['false_free_rate'])} | {fmt(r['count_mae'], 2)} |"
        )

    for title, base, variant in PAIRS:
        lines += [
            "",
            f"## {title} (`{base}` → `{variant}`)",
            "",
            "Corrigidos = vaga-quadros que a variante acerta e a base erra; introduzidos = o inverso.",
            "",
            "| Condição | F1 | Especificidade | Taxa falsa ocupada | Taxa falsa livre | FP | FN | EMA | "
            "Corrigidos | Introduzidos |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for pklot, name in CONDITIONS:
            rows = [r for r in decisions if pklot is None or r["condition"] == pklot]
            b = next(t for t in table if t["config"] == base and t["condition"] == name)
            v = next(t for t in table if t["config"] == variant and t["condition"] == name)
            fixed = sum(r[f"pred_{base}"] != r["label"] and r[f"pred_{variant}"] == r["label"] for r in rows)
            broken = sum(r[f"pred_{base}"] == r["label"] and r[f"pred_{variant}"] != r["label"] for r in rows)
            lines.append(
                f"| {name} | {fmt(b['f1'])} → {fmt(v['f1'])} | {fmt(b['specificity'])} → {fmt(v['specificity'])} | "
                f"{fmt(b['false_occupied_rate'])} → {fmt(v['false_occupied_rate'])} | "
                f"{fmt(b['false_free_rate'])} → {fmt(v['false_free_rate'])} | {b['fp']} → {v['fp']} | "
                f"{b['fn']} → {v['fn']} | {fmt(b['count_mae'], 2)} → {fmt(v['count_mae'], 2)} | {fixed} | {broken} |"
            )

    (TEST / "resultados_por_condicao.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Totais conferidos com metricas.csv.")
    print("Saídas: images/results/m3/teste/por_condicao.csv e resultados_por_condicao.md")


if __name__ == "__main__":
    main()
