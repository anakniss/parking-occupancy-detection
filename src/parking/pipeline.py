"""Pipeline de ocupação de vagas por comparação com uma imagem de referência (vaga livre).

Etapas, na ordem em que são aplicadas a cada quadro:

1. Pré-processamento: conversão para cinza e suavização gaussiana.
2. Compensação de iluminação (opcional): ganho global que iguala a mediana do
   quadro atual à mediana da referência.
3. Segmentação: diferença absoluta |atual - referência| e limiarização global.
4. Morfologia: abertura (remove pontos isolados) e fechamento (une fragmentos
   do mesmo veículo).
5. Análise de regiões: componentes conexos (vizinhança-8) dentro do polígono de
   cada vaga.
6. Descrição: atributos por vaga (área, perímetro, solidez, textura etc.).
7. Decisão: a vaga é ocupada se o maior componente cobre pelo menos
   `occupancy_threshold` da área da vaga.
"""
from __future__ import annotations

from dataclasses import dataclass, fields

import cv2
import numpy as np

from .dataset import Space

# Limiares do detector de bordas de Canny usados apenas no descritor de textura.
CANNY_LOW, CANNY_HIGH = 50, 150


@dataclass(frozen=True)
class PipelineConfig:
    blur_ksize: int = 5  # lado do kernel gaussiano (px, ímpar)
    gain_compensation: bool = False  # aplica o ganho global antes da diferença
    diff_threshold: int = 25  # limiar da diferença absoluta (níveis de cinza, 0-255)
    open_ksize: int = 0  # diâmetro do elemento estruturante da abertura (0 = desligada)
    close_ksize: int = 0  # diâmetro do elemento estruturante do fechamento (0 = desligado)
    min_component_area: int = 15  # componentes menores que isso (px) não são contados
    occupancy_threshold: float = 0.25  # fração da vaga coberta pelo maior componente

    @classmethod
    def from_dict(cls, values: dict) -> PipelineConfig:
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in values.items() if k in names})


@dataclass(frozen=True)
class SpaceRegion:
    """Polígono de uma vaga rasterizado dentro do seu retângulo envolvente."""

    id: int
    contour: np.ndarray  # polígono em coordenadas da imagem
    bbox: tuple[int, int, int, int]  # x, y, largura, altura
    mask: np.ndarray  # bool, mesmo tamanho do bbox; True dentro do polígono
    area: int  # pixels dentro do polígono


@dataclass
class Reference:
    """Imagem de referência (estacionamento livre) já pré-processada e mapa de vagas."""

    gray: np.ndarray
    median: float
    regions: list[SpaceRegion]


@dataclass
class FrameAnalysis:
    rows: list[dict]  # um dicionário de atributos por vaga
    gain: float
    steps: dict[str, np.ndarray] | None = None  # saídas intermediárias (quadro inteiro)


def build_regions(spaces: list[Space], shape: tuple[int, int]) -> list[SpaceRegion]:
    """Rasteriza os polígonos das vagas; o mapa é o mesmo para todos os quadros da câmera."""
    height, width = shape
    regions = []
    for space in spaces:
        x, y, w, h = cv2.boundingRect(space.contour)
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, width), min(y + h, height)
        mask = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillPoly(mask, [space.contour - np.array([x0, y0], np.int32)], 1)
        regions.append(
            SpaceRegion(space.id, space.contour, (x0, y0, x1 - x0, y1 - y0), mask.astype(bool), int(mask.sum()))
        )
    return regions


def preprocess(bgr: np.ndarray, cfg: PipelineConfig) -> np.ndarray:
    """Cinza + suavização gaussiana para atenuar ruído do sensor e artefatos de JPEG."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if cfg.blur_ksize > 1:
        gray = cv2.GaussianBlur(gray, (cfg.blur_ksize, cfg.blur_ksize), 0)
    return gray


def make_reference(bgr: np.ndarray, spaces: list[Space], cfg: PipelineConfig) -> Reference:
    gray = preprocess(bgr, cfg)
    return Reference(gray=gray, median=float(np.median(gray)), regions=build_regions(spaces, gray.shape))


def compensate_gain(gray: np.ndarray, reference_median: float) -> tuple[np.ndarray, float]:
    """Multiplica o quadro por g = mediana(referência) / mediana(atual), com saturação em 0-255."""
    gain = reference_median / max(float(np.median(gray)), 1.0)
    return cv2.convertScaleAbs(gray, alpha=gain), gain


def _disk(diameter: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (diameter, diameter))


def apply_morphology(binary: np.ndarray, open_ksize: int, close_ksize: int) -> tuple[np.ndarray, np.ndarray]:
    """Retorna (após abertura, após abertura + fechamento); tamanho <= 1 desliga a operação."""
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, _disk(open_ksize)) if open_ksize > 1 else binary
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, _disk(close_ksize)) if close_ksize > 1 else opened
    return opened, closed


def describe_space(
    region: SpaceRegion,
    foreground: np.ndarray,
    diff: np.ndarray,
    gray: np.ndarray,
    edges: np.ndarray,
    min_component_area: int,
) -> tuple[dict, np.ndarray]:
    """Rotula os componentes conexos dentro da vaga e calcula seus descritores.

    Retorna os atributos e a imagem de rótulos (recorte do bbox), usada nas figuras.
    """
    x, y, w, h = region.bbox
    inside = region.mask
    fg = (foreground[y : y + h, x : x + w] > 0) & inside
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(fg.astype(np.uint8), connectivity=8)
    areas = stats[1:, cv2.CC_STAT_AREA]

    largest_area, perimeter, solidity = 0, 0.0, 0.0
    if n_labels > 1:
        k = int(np.argmax(areas)) + 1
        largest_area = int(areas[k - 1])
        contours, _ = cv2.findContours((labels == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contour = max(contours, key=cv2.contourArea)
        perimeter = cv2.arcLength(contour, True)
        hull_area = cv2.contourArea(cv2.convexHull(contour))
        solidity = cv2.contourArea(contour) / hull_area if hull_area > 0 else 0.0

    row = {
        "space_id": region.id,
        "area_px": region.area,
        "frac_changed": fg.sum() / region.area,
        "n_components": int((areas >= min_component_area).sum()),
        "largest_area_px": largest_area,
        "largest_frac": largest_area / region.area,
        "largest_perimeter_px": perimeter,
        "largest_solidity": solidity,
        "mean_diff": float(diff[y : y + h, x : x + w][inside].mean()),
        "edge_density": float((edges[y : y + h, x : x + w][inside] > 0).mean()),
        "gray_std": float(gray[y : y + h, x : x + w][inside].std()),
    }
    return row, labels


def analyze(gray: np.ndarray, reference: Reference, cfg: PipelineConfig, keep_steps: bool = False) -> FrameAnalysis:
    """Aplica as etapas 2-7 a um quadro já pré-processado (`preprocess`)."""
    edges = cv2.Canny(gray, CANNY_LOW, CANNY_HIGH)
    compared, gain = compensate_gain(gray, reference.median) if cfg.gain_compensation else (gray, 1.0)
    diff = cv2.absdiff(compared, reference.gray)
    _, binary = cv2.threshold(diff, cfg.diff_threshold, 255, cv2.THRESH_BINARY)
    opened, closed = apply_morphology(binary, cfg.open_ksize, cfg.close_ksize)

    components = np.zeros(gray.shape, np.int32) if keep_steps else None
    next_label = 0
    rows = []
    for region in reference.regions:
        row, labels = describe_space(region, closed, diff, gray, edges, cfg.min_component_area)
        row["predicted"] = int(row["largest_frac"] >= cfg.occupancy_threshold)
        rows.append(row)
        if keep_steps:
            x, y, w, h = region.bbox
            view = components[y : y + h, x : x + w]
            view[labels > 0] = labels[labels > 0] + next_label
            next_label += int(labels.max())

    steps = None
    if keep_steps:
        steps = {
            "gray": gray,
            "compared": compared,
            "diff": diff,
            "binary": binary,
            "opened": opened,
            "closed": closed,
            "components": components,
            "edges": edges,
        }
    return FrameAnalysis(rows=rows, gain=gain, steps=steps)
