"""Executa o sistema final da M3 (ou outra configuração) em um dia inteiro, quadro a quadro.

Exemplos (a partir da raiz do repositório; o dia 2013-04-16 está todo na amostra versionada):
    python src/run_day.py --dia 2013-04-16 --quadro 07:15
    python src/run_day.py --dia 2013-04-16 --quadro 07:15 --variante B_M2

Entrada: os quadros do dia em `images/input/UFPR05/<condição>/<dia>/` (todas as condições),
a referência do dia (JSON do experimento) e os parâmetros congelados em
`models/sistema_final_m3.json`. `--variante` aceita as variantes congeladas da M3 (fixa,
adaptativa, dupla, dupla_LR) e as configurações da M2 (A_M2, B_M2 = baseline, C_M2), estas
com a referência fixa e os parâmetros de `configs/experimento_m2.json`.

Saídas em `images/results/m3/dia/<dia>/` para o sistema final e em
`images/results/m3/dia/<dia>_<variante>/` para as demais:

- `ocupacao.csv`: horário, vagas ocupadas/livres, taxa e, se houver rótulo, acertos;
- `fig_ocupacao.png`: ocupação ao longo do dia (prevista e, se houver, a do rótulo);
- `painel_<HHMM>.jpg` e `saida_<HHMM>.jpg` (com --quadro): etapas intermediárias e saída
  do quadro pedido, com a referência adaptativa no estado em que estava naquele momento.
"""
from __future__ import annotations

import argparse
import csv
import json

import cv2
import numpy as np

from parking import visualize as viz
from parking.classifier import LogisticModel
from parking.dataset import list_frames, load_spaces, parse_frame
from parking.experiment import REPO_ROOT, config_from, load_experiment, load_reference, read_image, resolve
from parking.pipeline import PipelineConfig, preprocess
from parking.sequence import DayProcessor, SequenceConfig

DEFAULT_EXPERIMENT = REPO_ROOT / "configs" / "experimento_m3.json"
FROZEN = REPO_ROOT / "models" / "sistema_final_m3.json"


def resolve_variant(name: str, frozen: dict, experiment: dict):
    """Configuração da variante pedida: (pipeline, sequência, tau ou None, modelo ou None)."""
    clf = frozen["classificador"]
    m2 = experiment["m2"]
    m2_names = {f"{n.split('_')[0]}_M2": n for n in [m2["baseline"], *m2["reavaliar"]]}
    if name in m2_names:
        cfg = config_from(load_experiment(m2["experimento"]), m2_names[name])
        return cfg, SequenceConfig(use_fixed=True, use_adaptive=False), cfg.occupancy_threshold, None
    m3_cfg = PipelineConfig.from_dict(frozen["pipeline"])
    if name == clf["nome"]:
        return m3_cfg, SequenceConfig.from_dict(frozen["variantes"][clf["base"]]), None, LogisticModel.from_dict(clf)
    if name in frozen["variantes"]:
        variant = frozen["variantes"][name]
        return m3_cfg, SequenceConfig.from_dict(variant), variant["tau"], None
    options = [*frozen["variantes"], clf["nome"], *m2_names]
    raise SystemExit(f"Variante '{name}' não existe. Opções: {', '.join(options)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sistema final da M3 aplicado a um dia do UFPR05.")
    parser.add_argument("--dia", required=True, help="AAAA-MM-DD")
    parser.add_argument("--quadro", help="HH:MM do quadro para salvar as etapas intermediárias")
    parser.add_argument("--variante", help="fixa, adaptativa, dupla, dupla_LR, A_M2, B_M2 ou C_M2 (padrão: o sistema final)")
    parser.add_argument("--reference", help="imagem do estacionamento vazio (padrão: a do dia no JSON)")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT))
    parser.add_argument("--out", default="images/results/m3/dia")
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    with open(FROZEN, encoding="utf-8") as f:
        frozen = json.load(f)
    name = args.variante or frozen["final"]
    cfg, seq, tau, model = resolve_variant(name, frozen, experiment)

    reference_path = args.reference or experiment["references"].get(args.dia)
    if reference_path is None:
        raise SystemExit(f"Sem referência para {args.dia}; informe --reference.")
    reference = load_reference(reference_path, cfg)
    reference_time = parse_frame(resolve(reference_path)).time[:5]  # do nome do arquivo, como nos quadros
    frames = [f for f in list_frames(resolve(experiment["dataset_root"]))
              if f.date == args.dia and f.path.resolve() != resolve(reference_path).resolve()]
    if not frames:
        raise SystemExit(f"Nenhum quadro de {args.dia} em {experiment['dataset_root']} (rode python src/get_data.py).")

    out_dir = resolve(args.out) / (args.dia if name == frozen["final"] else f"{args.dia}_{name}")
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = DayProcessor(reference, cfg, seq)
    target = args.quadro.replace(":", "") if args.quadro else None
    series = []
    for frame in frames:
        image = read_image(frame.path)
        gray = preprocess(image, cfg)
        keep = target is not None and frame.time.replace(":", "")[:4] == target
        adaptive_before = proc.adaptive_reference().gray if keep and seq.use_adaptive else None
        rows, steps = proc.step(gray, keep_steps=keep)
        if model is not None:
            predicted = model.predict(rows).tolist()
        else:
            predicted = [int(r["score"] >= tau) for r in rows]
        labels = {s.id: s.occupied for s in load_spaces(frame.xml_path)} if frame.xml_path.exists() else None
        occupied = sum(predicted)
        entry = {"frame_id": frame.id, "condicao": frame.condition, "horario": frame.time,
                 "ocupadas": occupied, "livres": len(rows) - occupied, "taxa_ocupacao": round(occupied / len(rows), 4)}
        if labels is not None:
            known = [(labels.get(r["space_id"]), p) for r, p in zip(rows, predicted)]
            entry["ocupadas_rotulo"] = sum(1 for lab, _ in known if lab == 1)
            entry["acertos"] = sum(1 for lab, p in known if lab is not None and lab == p)
            entry["vagas_rotuladas"] = sum(1 for lab, _ in known if lab is not None)
        series.append(entry)

        if keep:
            shown = [{"space_id": r["space_id"], "predicted": p} for r, p in zip(rows, predicted)]
            summary = [f"{name} | {frame.id}", f"Ocupadas: {occupied}  Livres: {len(rows) - occupied}  "
                       f"Taxa: {100 * occupied / len(rows):.1f}%"]
            if labels is not None:
                summary.append(f"Rotulo XML: {entry['ocupadas_rotulo']} ocupadas | acertos {entry['acertos']}/{entry['vagas_rotuladas']}")
            output = viz.draw_result(image, reference.regions, shown, labels, summary)
            hhmm = frame.time[:5].replace(":", "")
            cv2.imwrite(str(out_dir / f"saida_{hhmm}.jpg"), output, [cv2.IMWRITE_JPEG_QUALITY, 88])
            reference_title = "Referência fixa" if seq.use_fixed else "Referência inicial"
            panel = [("Entrada", viz.draw_spaces(image, reference.regions)),
                     (f"{reference_title} ({reference_time})", reference.gray),
                     ("Referência adaptativa (antes do quadro)", adaptive_before)]
            for key, title in (("fix", "fixa"), ("ad", "adaptativa")):
                if key in steps:
                    panel += [(f"Diferença |atual − {title}|", viz.diff_view(steps[key]["diff"])),
                              (f"Máscara após morfologia ({title})", viz.mask_view(steps[key]["closed"], reference.regions))]
            if model is not None:
                rule = "regressão logística"
            elif seq.use_fixed and seq.use_adaptive:
                rule = f"regra: menor fração ≥ {tau:.2f}".replace(".", ",")
            else:
                rule = f"regra: fração ≥ {tau:.2f}".replace(".", ",")
            panel.append((f"Saída ({rule})", output))
            viz.save_panel([(t, im) for t, im in panel if im is not None], out_dir / f"painel_{hhmm}.jpg")

    with open(out_dir / "ocupacao.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(series[0]))
        writer.writeheader()
        writer.writerows(series)
    day = {"title": f"{args.dia} · {name}", "times": [s["horario"] for s in series],
           "true": [s.get("ocupadas_rotulo", np.nan) for s in series], name: [s["ocupadas"] for s in series]}
    viz.plot_counts([day], [name], out_dir / "fig_ocupacao.png")

    total = sum(s.get("vagas_rotuladas", 0) for s in series)
    correct = sum(s.get("acertos", 0) for s in series)
    print(f"Dia {args.dia}: {len(series)} quadros ({series[0]['horario'][:5]}–{series[-1]['horario'][:5]}), "
          f"sistema '{name}'.")
    if total:
        print(f"Acertos contra o XML: {correct}/{total} vaga-quadros ({100 * correct / total:.2f}%).")
    if target and not any(s["horario"].replace(":", "")[:4] == target for s in series):
        print(f"AVISO: nenhum quadro às {args.quadro}.")
    shown = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"Saídas em: {shown.as_posix()}")


if __name__ == "__main__":
    main()
