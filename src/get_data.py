"""Baixa do PKLot (Hugging Face) os dias do UFPR05 usados na M3 que não são versionados.

Exemplo (a partir da raiz do repositório):
    python src/get_data.py

O que o script faz:
1. baixa `samples.json` (anotações da versão FiftyOne do PKLot, 267 MB) na revisão
   fixada no JSON do experimento e confere o SHA-256;
2. seleciona as imagens do UFPR05 das pastas listadas em `dados.baixar`
   (`<Condição>/<AAAA-MM-DD>`), isto é, todos os quadros daquele dia com aquela condição;
3. baixa cada JPEG e grava ao lado um XML no formato do PKLot original
   (`<space id occupied>` + `<contour>`), reconstruído a partir dos polígonos normalizados.

A conversão foi conferida contra os 140 XMLs originais da amostra versionada: polígonos
e rótulos idênticos (ver `tests/test_dados.py`). O XML gerado não traz o `rotatedRect`
do original, que o pipeline não usa.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from parking.experiment import REPO_ROOT, load_experiment, resolve

DEFAULT_EXPERIMENT = REPO_ROOT / "configs" / "experimento_m3.json"
BASE_URL = "https://huggingface.co/datasets/{repo}/resolve/{revision}/{path}"
WIDTH, HEIGHT = 1280, 720  # resolução de todas as imagens do UFPR05
STATUS = {"occupied": "1", "not occupied": "0"}  # "unknown" -> sem atributo, como no original


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as response, open(tmp, "wb") as f:
        while chunk := response.read(1 << 20):
            f.write(chunk)
    tmp.replace(dest)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def iter_samples(path: Path):
    """Percorre a lista `samples` do JSON um objeto por vez (evita carregar 267 MB de objetos)."""
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    pos = text.index("[", text.index('"samples"')) + 1
    while True:
        while text[pos] in " \r\n\t,":
            pos += 1
        if text[pos] == "]":
            return
        sample, pos = decoder.raw_decode(text, pos)
        yield sample


def frame_id(sample: dict) -> str:
    return Path(sample["filepath"]).stem


def to_xml(sample: dict) -> str:
    lines = [f'<parking id="{sample["source"]}">']
    spaces = sorted(sample["parking_spaces"]["polylines"], key=lambda p: p["space_id"])
    for space in spaces:
        occupied = STATUS.get(space["occupancy_status"])
        attr = f' occupied="{occupied}"' if occupied is not None else ""
        lines.append(f'  <space id="{space["space_id"]}"{attr}>')
        lines.append("    <contour>")
        for x, y in space["points"][0]:
            lines.append(f'      <point x="{round(x * WIDTH)}" y="{round(y * HEIGHT)}" />')
        lines.append("    </contour>")
        lines.append("  </space>")
    lines.append("</parking>")
    return "\n".join(lines) + "\n"


def load_index(experiment: dict, cache: Path) -> dict[tuple[str, str], list[dict]]:
    """Amostras do lote configurado, agrupadas por (condição, dia)."""
    source = experiment["dados"]["fonte"]
    annotations = cache / f"samples_{source['revision'][:12]}.json"
    if not annotations.exists() or sha256(annotations) != source["samples_sha256"]:
        url = BASE_URL.format(repo=source["repo"], revision=source["revision"], path="samples.json")
        print(f"Baixando anotações ({url}) ...", flush=True)
        download(url, annotations)
        digest = sha256(annotations)
        if digest != source["samples_sha256"]:
            raise SystemExit(f"SHA-256 inesperado para samples.json: {digest}")
    index = defaultdict(list)
    for sample in iter_samples(annotations):
        if sample["source"] != source["lot"]:
            continue
        name = frame_id(sample)
        index[(sample["weather"]["label"].capitalize(), name[:10])].append(sample)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa os dias do PKLot/UFPR05 usados na M3.")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT), help="arquivo JSON do experimento")
    parser.add_argument("--cache", default=".cache/pklot", help="pasta para o samples.json (fora do Git)")
    parser.add_argument("--workers", type=int, default=8, help="downloads simultâneos")
    args = parser.parse_args()

    experiment = load_experiment(args.experiment)
    source = experiment["dados"]["fonte"]
    root = resolve(experiment["dataset_root"])
    index = load_index(experiment, resolve(args.cache))

    pending = []
    total = 0
    for folder in experiment["dados"]["baixar"]:
        condition, day = folder.split("/")
        samples = sorted(index.get((condition, day), []), key=frame_id)
        if not samples:
            raise SystemExit(f"Nenhuma imagem do lote {source['lot']} em {folder}.")
        for sample in samples:
            jpg = root / folder / Path(sample["filepath"]).name
            jpg.parent.mkdir(parents=True, exist_ok=True)
            jpg.with_suffix(".xml").write_text(to_xml(sample), encoding="utf-8")
            if not jpg.exists():
                url = BASE_URL.format(repo=source["repo"], revision=source["revision"], path=sample["filepath"])
                pending.append((url, jpg))
        total += len(samples)
        print(f"{folder}: {len(samples)} imagens")

    if pending:
        print(f"Baixando {len(pending)} imagens ({args.workers} conexões) ...", flush=True)
        with ThreadPoolExecutor(args.workers) as pool:
            for done, _ in enumerate(pool.map(lambda job: download(*job), pending), 1):
                if done % 100 == 0:
                    print(f"  {done}/{len(pending)}", flush=True)
    print(f"Total: {total} imagens ({len(pending)} baixadas agora) em {root.relative_to(REPO_ROOT).as_posix()}/")


if __name__ == "__main__":
    sys.exit(main())
