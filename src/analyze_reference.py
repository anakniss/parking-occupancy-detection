"""X3 — Quanto o baseline depende da foto do estacionamento vazio (só dados de desenvolvimento).

    python src/analyze_reference.py

Usa só a amostra versionada da M2 (manhãs de 13/04 chuva, 14/04 nublado e 16/04 sol), que na M3 é
desenvolvimento; os dias de teste não são lidos. O sistema avaliado é o baseline `B_M2` congelado
(configuração B da M2: T = 25, abertura 3, fechamento 7, τ = 0,24), sem nenhum reajuste. Só a imagem
de referência muda:

- `mesmo dia`: o primeiro quadro vazio do próprio dia (a regra usada em todo o projeto);
- `mesmo dia, mais tarde`: o último quadro vazio da manhã do próprio dia, quando existe;
- `outro dia`: o quadro de referência de cada um dos outros dois dias (mesma câmera, outro clima).

Todos os quadros que servem de referência em alguma linha ficam fora da avaliação, para que as
linhas usem exatamente os mesmos quadros. Também conta, em cada dia, quantos quadros têm as 40
vagas livres (a janela disponível para registrar a referência).

Saídas em `images/results/m3/referencia/`: `sensibilidade_referencia.csv`, `janela_vazio.csv` e
`resultados_referencia.md`.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from parking.dataset import list_frames, load_spaces
from parking.experiment import REPO_ROOT, config_from, load_experiment, load_reference, read_image, resolve, write_csv
from parking.metrics import classification_metrics, count_metrics
from parking.pipeline import analyze, preprocess

M2 = REPO_ROOT / "configs" / "experimento_m2.json"
ROOT = "images/input/UFPR05"
SAMPLE = {"2013-04-13": "Rainy/2013-04-13", "2013-04-14": "Cloudy/2013-04-14", "2013-04-16": "Sunny/2013-14-16"}
CONDITION = {"2013-04-13": "chuva", "2013-04-14": "nublado", "2013-04-16": "sol"}


def empty_frames(frames) -> list:
    return [f for f in frames if all(s.occupied == 0 for s in load_spaces(f.xml_path))]


def fmt(value, digits: int = 3) -> str:
    if isinstance(value, float):
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sensibilidade do baseline à imagem de referência (desenvolvimento).")
    parser.add_argument("--out", default="images/results/m3/referencia", help="pasta de saída")
    args = parser.parse_args()
    out_dir = resolve(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    experiment = load_experiment(M2)
    cfg = config_from(experiment, "B_morfologia")
    standard = experiment["references"]

    frames_by_day = {d: list_frames(resolve(ROOT) / folder) for d, folder in SAMPLE.items()}

    window = []
    candidates = {}  # nome -> (caminho, dia da referência)
    for day, frames in frames_by_day.items():
        empty = empty_frames(frames)
        window.append({
            "date": day, "condition": CONDITION[day], "frames_in_sample": len(frames), "empty_frames": len(empty),
            "first_empty": empty[0].time if empty else "", "last_empty": empty[-1].time if empty else "",
        })
        candidates[f"{day} {Path(standard[day]).stem[11:16].replace('_', ':')}"] = (standard[day], day)
        if len(empty) > 1:
            last = empty[-1]
            candidates[f"{day} {last.time[:5]}"] = (str(last.path), day)

    reference_ids = {Path(path).stem for path, _ in candidates.values()}
    references = {name: load_reference(path, cfg) for name, (path, _) in candidates.items()}

    results = []
    for day, frames in frames_by_day.items():
        evaluated = [f for f in frames if f.id not in reference_ids]
        grays = [preprocess(read_image(f.path), cfg) for f in evaluated]
        labels = [{s.id: s.occupied for s in load_spaces(f.xml_path)} for f in evaluated]
        for name, (path, ref_day) in candidates.items():
            if ref_day == day:
                kind = "mesmo dia" if Path(path).stem == Path(standard[day]).stem else "mesmo dia, mais tarde"
            else:
                kind = "outro dia"
            y_true, y_pred, per_frame = [], [], []
            for gray, label in zip(grays, labels):
                rows = analyze(gray, references[name], cfg).rows
                true_count = pred_count = 0
                for row in rows:
                    truth = label.get(row["space_id"])
                    if truth is None:
                        continue
                    y_true.append(truth)
                    y_pred.append(row["predicted"])
                    true_count += truth
                    pred_count += row["predicted"]
                per_frame.append((true_count, pred_count))
            m = classification_metrics(y_true, y_pred)
            counts = np.array(per_frame)
            c = count_metrics(counts[:, 0], counts[:, 1], 40)
            results.append({
                "target_date": day, "target_condition": CONDITION[day], "reference": name,
                "reference_condition": CONDITION[ref_day], "kind": kind, "frames": len(evaluated),
                **m,
                "false_occupied_rate": 1 - m["specificity"] if not np.isnan(m["specificity"]) else float("nan"),
                "false_free_rate": 1 - m["recall"] if not np.isnan(m["recall"]) else float("nan"),
                "count_mae": c["count_mae"], "count_bias": c["count_bias"], "count_max_abs": c["count_max_abs"],
            })
            print(f"{day} ({CONDITION[day]}) ← ref {name} [{kind}]: FP {m['fp']}, FN {m['fn']}, "
                  f"F1 {m['f1']:.3f}, EMA {c['count_mae']:.2f}")

    write_csv(out_dir / "sensibilidade_referencia.csv", results)
    write_csv(out_dir / "janela_vazio.csv", window)

    order = {"mesmo dia": 0, "mesmo dia, mais tarde": 1, "outro dia": 2}
    lines = [
        "# X3 — Sensibilidade do baseline à referência vazia (gerado por `src/analyze_reference.py`)",
        "",
        "Arquivo gerado automaticamente; não edite à mão. Só a amostra da M2 (desenvolvimento da M3); "
        "baseline `B_M2` congelado (T = 25, abertura 3, fechamento 7, τ = 0,24), sem reajuste. "
        "Classe positiva = vaga ocupada. Taxa de falsa ocupada = FP / (FP + VN); taxa de falsa livre = FN / (FN + VP). "
        f"Quadros que servem de referência ficam fora da avaliação ({len(reference_ids)} quadros).",
        "",
        "## Janela com o estacionamento vazio",
        "",
        "| Dia | Condição | Quadros na amostra | Quadros com as 40 vagas livres | Primeiro | Último |",
        "|---|---|---|---|---|---|",
    ]
    lines += [f"| {w['date']} | {w['condition']} | {w['frames_in_sample']} | {w['empty_frames']} | "
              f"{w['first_empty']} | {w['last_empty']} |" for w in window]
    lines += [
        "",
        "## Indicadores por dia avaliado e referência",
        "",
        "| Dia avaliado | Referência | Tipo | Quadros | VP | FP | FN | VN | F1 | Especificidade | "
        "Taxa falsa ocupada | Taxa falsa livre | EMA contagem | Erro máx. |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    by_day = defaultdict(list)
    for r in results:
        by_day[r["target_date"]].append(r)
    for day, rows in by_day.items():
        for r in sorted(rows, key=lambda r: (order[r["kind"]], r["reference"])):
            lines.append(
                f"| {day} ({r['target_condition']}) | {r['reference']} ({r['reference_condition']}) | {r['kind']} | "
                f"{r['frames']} | {r['tp']} | {r['fp']} | {r['fn']} | {r['tn']} | {fmt(r['f1'])} | "
                f"{fmt(r['specificity'])} | {fmt(r['false_occupied_rate'])} | {fmt(r['false_free_rate'])} | "
                f"{fmt(r['count_mae'], 2)} | {fmt(float(r['count_max_abs']), 0)} |"
            )
    (out_dir / "resultados_referencia.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saídas em: {out_dir.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
