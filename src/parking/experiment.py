"""Utilitários compartilhados pelos scripts: configuração, caminhos e referências."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2
import numpy as np

from .dataset import load_spaces, parse_frame
from .pipeline import PipelineConfig, Reference, make_reference

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT = REPO_ROOT / "configs" / "experimento_m2.json"


def resolve(path: str | Path) -> Path:
    """Caminhos relativos são resolvidos a partir da raiz do repositório."""
    path = Path(path)
    return path if path.is_absolute() else REPO_ROOT / path


def load_experiment(path: str | Path = DEFAULT_EXPERIMENT) -> dict:
    with open(resolve(path), encoding="utf-8") as f:
        return json.load(f)


def config_from(experiment: dict, name: str) -> PipelineConfig:
    if name not in experiment["configs"]:
        raise SystemExit(f"Configuração '{name}' não existe. Opções: {', '.join(experiment['configs'])}")
    return PipelineConfig.from_dict(experiment["configs"][name])


def read_image(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(resolve(path)))
    if image is None:
        raise SystemExit(f"Não foi possível ler a imagem: {path}")
    return image


def load_reference(path: str | Path, cfg: PipelineConfig) -> Reference:
    """Referência = quadro do estacionamento livre; o XML dela fornece o mapa de vagas."""
    path = resolve(path)
    return make_reference(read_image(path), load_spaces(parse_frame(path).xml_path), cfg)


def write_csv(path: Path, rows: list[dict]) -> None:
    def fmt(value):
        return round(value, 4) if isinstance(value, float) else value

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: fmt(v) for k, v in row.items()} for row in rows)
