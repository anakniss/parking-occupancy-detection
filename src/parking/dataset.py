"""Leitura do subconjunto PKLot/UFPR05: imagens, anotações XML e organização por dia."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Data e hora vêm do nome do arquivo (AAAA-MM-DD_HH_MM_SS.jpg), e não do nome
# da pasta: na amostra, a pasta do dia ensolarado está nomeada "2013-14-16".
_STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{2})_(\d{2})_(\d{2})$")


@dataclass(frozen=True)
class Space:
    """Uma vaga anotada no XML do PKLot."""

    id: int
    occupied: int | None  # 1 = ocupada, 0 = livre, None = sem rótulo
    contour: np.ndarray  # polígono da vaga, shape (N, 2), coordenadas em pixels


@dataclass(frozen=True)
class Frame:
    """Uma imagem do estacionamento e seus metadados."""

    path: Path
    condition: str  # condição climática atribuída pelo PKLot (Sunny, Cloudy, Rainy)
    date: str  # AAAA-MM-DD
    time: str  # HH:MM:SS

    @property
    def id(self) -> str:
        return self.path.stem

    @property
    def xml_path(self) -> Path:
        return self.path.with_suffix(".xml")


def load_spaces(xml_path: str | Path) -> list[Space]:
    """Lê as vagas (polígono e rótulo) de um XML do PKLot, ordenadas por id."""
    root = ET.parse(xml_path).getroot()
    spaces = []
    for node in root.iter("space"):
        points = [(int(p.get("x")), int(p.get("y"))) for p in node.find("contour").iter("point")]
        occupied = node.get("occupied")
        spaces.append(
            Space(
                id=int(node.get("id")),
                occupied=None if occupied is None else int(occupied),
                contour=np.array(points, dtype=np.int32),
            )
        )
    return sorted(spaces, key=lambda s: s.id)


def parse_frame(path: str | Path) -> Frame:
    """Cria um Frame a partir do caminho <lote>/<condição>/<dia>/<AAAA-MM-DD_HH_MM_SS>.jpg."""
    path = Path(path)
    match = _STAMP.match(path.stem)
    if match is None:
        raise ValueError(f"Nome de arquivo fora do padrão PKLot: {path.name}")
    date, hh, mm, ss = match.groups()
    return Frame(path=path, condition=path.parent.parent.name, date=date, time=f"{hh}:{mm}:{ss}")


def list_frames(root: str | Path) -> list[Frame]:
    """Lista todas as imagens .jpg sob `root`, em ordem cronológica."""
    frames = [parse_frame(p) for p in Path(root).rglob("*.jpg")]
    return sorted(frames, key=lambda f: (f.date, f.time))
