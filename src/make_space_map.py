"""Mapa de vagas e formato das máscaras, para documentar a entrada espacial do pipeline.

    python src/make_space_map.py

Usa só a amostra versionada (offline). Saídas em `images/results/m3/mapa/`:

- `mapa_vagas.jpg`: quadro de referência de 2013-04-14 06:40 com o polígono e o id de cada vaga;
- `mapa_vagas.csv`: por vaga, os vértices do polígono, o retângulo envolvente, a área rasterizada
  e o centroide (coordenadas em pixels da imagem 1280x720, origem no canto superior esquerdo);
- `mascara_vagas.png`: imagem de rótulos 1280x720 em uint8, 0 = fora de qualquer vaga e
  k = pixel da vaga k (1 a 40). É a rasterização usada pelo pipeline (`build_regions`);
- `fig_mascaras.jpg`: as máscaras de uma vaga no quadro 2013-04-14 10:00 (vaga 8, ocupada),
  da imagem ao maior componente, com o tipo e os valores de cada uma.

O mapa é o mesmo em todos os quadros da câmera: os polígonos dos XMLs do UFPR05 são idênticos
entre os dias da amostra, o que o script confere antes de gerar as saídas.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np

from parking import visualize as viz
from parking.dataset import list_frames, load_spaces
from parking.experiment import REPO_ROOT, config_from, load_experiment, load_reference, read_image, resolve
from parking.pipeline import analyze, build_regions, preprocess

M2 = REPO_ROOT / "configs" / "experimento_m2.json"
REFERENCE = "images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_06_40_00.jpg"
EXAMPLE = "images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_10_00_04.jpg"
EXAMPLE_SPACE = 8
SAMPLE_FOLDERS = ["Cloudy/2013-04-14", "Sunny/2013-14-16", "Rainy/2013-04-13"]


def check_same_map(root: Path) -> int:
    """Confere que todos os XMLs da amostra têm os mesmos polígonos; retorna quantos foram lidos."""
    first = None
    count = 0
    for folder in SAMPLE_FOLDERS:
        for frame in list_frames(root / folder):
            polygons = {s.id: s.contour.tolist() for s in load_spaces(frame.xml_path)}
            if first is None:
                first = polygons
            elif polygons != first:
                raise SystemExit(f"O mapa de vagas de {frame.id} difere do primeiro XML da amostra.")
            count += 1
    return count


def draw_map(image: np.ndarray, regions) -> np.ndarray:
    out = image.copy()
    overlay = image.copy()
    for region in regions:
        cv2.fillPoly(overlay, [region.contour], viz._bgr(viz.SERIES[0]))
    out = cv2.addWeighted(overlay, 0.22, out, 0.78, 0)
    for region in regions:
        cv2.polylines(out, [region.contour], True, (255, 255, 255), 2, cv2.LINE_AA)
    for region in regions:
        cx, cy = region.contour.mean(0).astype(int)
        text = str(region.id)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        org = (int(cx - tw / 2), int(cy + th / 2))
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return out


def mask_figure(out_path: Path) -> dict:
    experiment = load_experiment(M2)
    cfg = config_from(experiment, "B_morfologia")
    reference = load_reference(REFERENCE, cfg)
    image = read_image(EXAMPLE)
    result = analyze(preprocess(image, cfg), reference, cfg, keep_steps=True)
    steps = result.steps
    region = next(r for r in reference.regions if r.id == EXAMPLE_SPACE)
    row = next(r for r in result.rows if r["space_id"] == EXAMPLE_SPACE)

    margin = 12
    x, y, w, h = region.bbox
    x0, y0 = max(x - margin, 0), max(y - margin, 0)
    x1, y1 = min(x + w + margin, image.shape[1]), min(y + h + margin, image.shape[0])

    def cut(img):
        return img[y0:y1, x0:x1]

    polygon = np.zeros(image.shape[:2], np.uint8)
    polygon[y : y + h, x : x + w][region.mask] = 255
    inside = (steps["closed"] > 0) & (polygon > 0)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inside.astype(np.uint8), connectivity=8)
    largest = np.zeros_like(polygon)
    if n_labels > 1:
        k = int(np.argmax(stats[1:, cv2.CC_STAT_AREA])) + 1
        largest[labels == k] = 255

    contour = region.contour - np.array([x0, y0], np.int32)

    def outline(gray_or_bgr):
        view = gray_or_bgr if gray_or_bgr.ndim == 3 else cv2.cvtColor(gray_or_bgr, cv2.COLOR_GRAY2BGR)
        view = view.copy()
        cv2.polylines(view, [contour], True, viz._bgr(viz.SERIES[0]), 1, cv2.LINE_AA)
        return view

    panels = [
        ("1. Quadro atual (BGR, uint8)", outline(cut(image))),
        ("2. Polígono rasterizado\n(bool; aqui 0/255)", cut(polygon)),
        (f"3. Diferença |atual − ref.|\n(uint8, 0–255; escala 0–100)", outline(cut(viz.diff_view(steps["diff"])))),
        (f"4. Limiarizada, T = {cfg.diff_threshold}\n(uint8, 0 ou 255)", outline(cut(steps["binary"]))),
        (f"5. Abertura {cfg.open_ksize} + fechamento {cfg.close_ksize}\n(uint8, 0 ou 255)", outline(cut(steps["closed"]))),
        (f"6. Maior componente na vaga\nfração = {row['largest_frac']:.2f} ≥ τ = {cfg.occupancy_threshold:.2f}",
         outline(cut(largest))),
    ]
    viz.save_panel(panels, out_path, cols=3)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o mapa de vagas e a figura do formato das máscaras.")
    parser.add_argument("--out", default="images/results/m3/mapa", help="pasta de saída")
    args = parser.parse_args()
    out_dir = resolve(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    n_xml = check_same_map(resolve("images/input/UFPR05"))
    image = read_image(REFERENCE)
    spaces = load_spaces(Path(resolve(REFERENCE)).with_suffix(".xml"))
    regions = build_regions(spaces, image.shape[:2])

    cv2.imwrite(str(out_dir / "mapa_vagas.jpg"), draw_map(image, regions), [cv2.IMWRITE_JPEG_QUALITY, 90])

    label_image = np.zeros(image.shape[:2], np.uint8)
    overlap = 0
    for region in regions:
        x, y, w, h = region.bbox
        view = label_image[y : y + h, x : x + w]
        overlap += int(((view > 0) & region.mask).sum())
        view[region.mask] = region.id
    cv2.imwrite(str(out_dir / "mascara_vagas.png"), label_image)

    with open(out_dir / "mapa_vagas.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["space_id", "n_vertices", "vertices_xy", "bbox_x", "bbox_y", "bbox_w", "bbox_h",
                         "area_px", "centroid_x", "centroid_y"])
        for region in regions:
            vertices = ";".join(f"{px} {py}" for px, py in region.contour.tolist())
            cx, cy = region.contour.mean(0)
            writer.writerow([region.id, len(region.contour), vertices, *region.bbox, region.area,
                             round(float(cx), 1), round(float(cy), 1)])

    row = mask_figure(out_dir / "fig_mascaras.jpg")

    areas = [r.area for r in regions]
    print(f"XMLs conferidos: {n_xml} (mesmo mapa em todos)")
    print(f"Vagas: {len(regions)} | área por vaga: {min(areas)}–{max(areas)} px (mediana {int(np.median(areas))})")
    print(f"Pixels em mais de uma vaga (sobreposição de polígonos): {overlap}")
    print(f"Exemplo: vaga {EXAMPLE_SPACE} em {Path(EXAMPLE).stem}: fração do maior componente = "
          f"{row['largest_frac']:.3f} -> {'ocupada' if row['predicted'] else 'livre'}")
    print(f"Saídas em: {out_dir.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
