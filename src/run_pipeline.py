"""Executa o pipeline em uma imagem e salva todas as saídas intermediárias.

Exemplo (a partir da raiz do repositório):
    python src/run_pipeline.py --image images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_10_00_04.jpg
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from parking import visualize as viz
from parking.dataset import load_spaces, parse_frame
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
from parking.pipeline import analyze, preprocess

MASK_STAGES = {"05_limiarizada", "06_abertura", "07_fechamento", "08_componentes"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Classifica as vagas de uma imagem do PKLot/UFPR05.")
    parser.add_argument("--image", required=True, help="imagem .jpg a analisar")
    parser.add_argument("--reference", help="imagem do estacionamento livre (padrão: a do mesmo dia no JSON)")
    parser.add_argument("--config", help="nome da configuração no JSON (padrão: default_config)")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT), help="arquivo JSON do experimento")
    parser.add_argument("--out", default="images/results/exemplo", help="pasta de saída")
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    name = args.config or experiment["default_config"]
    cfg = config_from(experiment, name)

    frame = parse_frame(resolve(args.image))
    reference_path = args.reference or experiment["references"].get(frame.date)
    if reference_path is None:
        raise SystemExit(f"Sem referência para {frame.date}; informe --reference.")
    reference = load_reference(reference_path, cfg)

    image = read_image(frame.path)
    result = analyze(preprocess(image, cfg), reference, cfg, keep_steps=True)
    steps = result.steps

    labels = None
    if frame.xml_path.exists():
        labels = {s.id: s.occupied for s in load_spaces(frame.xml_path)}
        for row in result.rows:
            row["label"] = labels.get(row["space_id"])

    total = len(result.rows)
    occupied = sum(row["predicted"] for row in result.rows)
    summary = [
        f"Vagas: {total}  Ocupadas: {occupied}  Livres: {total - occupied}",
        f"Ocupacao: {100 * occupied / total:.1f}%",
    ]
    correct = None
    if labels is not None:
        correct = sum(row["predicted"] == row["label"] for row in result.rows if row["label"] is not None)
        summary.append(f"Rotulo XML: {sum(v == 1 for v in labels.values())} ocupadas | acertos {correct}/{total}")

    out_dir = resolve(args.out) / frame.id
    out_dir.mkdir(parents=True, exist_ok=True)
    regions = reference.regions
    stages = [
        ("01_entrada", "Entrada + mapa de vagas (XML)", viz.draw_spaces(image, regions)),
        ("02_referencia", f"Referência livre ({Path(reference_path).stem})", reference.gray),
        (
            "03_preprocessada",
            f"Cinza + gaussiano {cfg.blur_ksize}x{cfg.blur_ksize}"
            + (f" + ganho {result.gain:.2f}" if cfg.gain_compensation else ""),
            steps["compared"],
        ),
        ("04_diferenca", "Diferença absoluta |atual - ref.|", viz.diff_view(steps["diff"])),
        ("05_limiarizada", f"Limiarização global (T = {cfg.diff_threshold})", viz.mask_view(steps["binary"], regions)),
        ("06_abertura", f"Abertura (disco {cfg.open_ksize} px)", viz.mask_view(steps["opened"], regions)),
        ("07_fechamento", f"Fechamento (disco {cfg.close_ksize} px)", viz.mask_view(steps["closed"], regions)),
        (
            "08_componentes",
            "Componentes conexos por vaga (fração do maior)",
            viz.components_view(steps["components"], regions, result.rows),
        ),
        (
            "09_saida",
            f"Saída (τ = {cfg.occupancy_threshold:.2f}): verde livre, vermelho ocupada",
            viz.draw_result(image, regions, result.rows, labels, summary),
        ),
    ]
    for filename, _, img in stages:
        # máscaras em PNG (sem perdas e pequenas); fotos em JPEG para não inflar o repositório
        if filename in MASK_STAGES:
            cv2.imwrite(str(out_dir / f"{filename}.png"), img)
        else:
            cv2.imwrite(str(out_dir / f"{filename}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    viz.save_panel([(title, img) for _, title, img in stages], out_dir / "painel.jpg")
    write_csv(out_dir / "vagas.csv", result.rows)
    with open(out_dir / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "image": frame.id,
                "condition": frame.condition,
                "reference": Path(reference_path).stem,
                "config": name,
                "parameters": cfg.__dict__,
                "gain": result.gain,
                "spaces": total,
                "occupied": occupied,
                "free": total - occupied,
                "occupancy_rate": occupied / total,
                "labeled_occupied": None if labels is None else sum(v == 1 for v in labels.values()),
                "correct": correct,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Imagem: {frame.id} ({frame.condition}, {frame.date} {frame.time})")
    print(f"Referência: {Path(reference_path).stem}")
    print(
        f"Configuração: {name} (T = {cfg.diff_threshold}, tau = {cfg.occupancy_threshold:.2f}, "
        f"abertura = {cfg.open_ksize}, fechamento = {cfg.close_ksize}, ganho = {cfg.gain_compensation})"
    )
    print(f"Vagas analisadas: {total} | Ocupadas: {occupied} | Livres: {total - occupied} | "
          f"Ocupação: {100 * occupied / total:.1f}%")
    if labels is not None:
        print(f"Rótulos do XML: {sum(v == 1 for v in labels.values())} ocupadas | acertos: {correct}/{total}")
    shown = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"Saídas em: {shown.as_posix()}")


if __name__ == "__main__":
    main()
