"""Processamento de um dia em ordem cronológica com referência fixa e referência adaptativa (M3).

Na M2, cada quadro era comparado com uma única referência: o estacionamento vazio no início
da manhã. Ao longo do dia a iluminação muda (sol, sombras, asfalto secando) e essa
referência deixa de representar a vaga livre, o que gera falsos positivos.

Na M3, o sistema mantém duas referências por dia:

- **fixa**: o primeiro quadro do dia com o estacionamento vazio (a mesma da M2);
- **adaptativa**: começa igual à fixa e, depois de cada quadro, os pixels das vagas julgadas
  livres com folga são misturados a ela por média móvel (atualização seletiva):

      ref <- (1 - alpha) * ref + alpha * quadro      (só dentro das vagas livres)

  Vagas ocupadas não são atualizadas, para que o veículo não seja incorporado ao fundo.

A vaga é comparada com as duas referências pelo mesmo pipeline da M2 (diferença, limiar,
abertura, fechamento e componentes). O escore de ocupação é a **menor** das duas frações
do maior componente: a vaga só é considerada ocupada se diferir das duas referências. A
justificativa é que um veículo difere de qualquer imagem da vaga vazia, enquanto uma mudança
de iluminação costuma afetar só uma delas (a fixa, com a deriva ao longo do dia; a
adaptativa, quando uma sombra absorvida desaparece de repente).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pipeline import FrameAnalysis, PipelineConfig, Reference, analyze

# Descritores da M2 que dependem da referência; recebem o sufixo _fix ou _ad.
REFERENCE_DESCRIPTORS = ("frac_changed", "n_components", "largest_frac", "largest_solidity", "mean_diff")
# Descritores calculados só no quadro atual (iguais para as duas referências).
FRAME_DESCRIPTORS = ("area_px", "edge_density", "gray_std")


@dataclass(frozen=True)
class SequenceConfig:
    use_fixed: bool = True  # compara com a referência fixa (início do dia)
    use_adaptive: bool = True  # compara com a referência adaptativa
    alpha: float = 0.25  # taxa da média móvel da referência adaptativa (0-1)
    free_max: float = 0.20  # a vaga atualiza a referência se escore < free_max (folga abaixo de tau)

    def __post_init__(self):
        if not (self.use_fixed or self.use_adaptive):
            raise ValueError("Pelo menos uma referência deve estar ativa.")

    @classmethod
    def from_dict(cls, values: dict) -> SequenceConfig:
        names = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in values.items() if k in names})


def ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Correlação cruzada normalizada entre dois vetores de pixels (invariante a ganho e deslocamento)."""
    a = a.astype(np.float64) - a.mean()
    b = b.astype(np.float64) - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


class DayProcessor:
    """Classifica os quadros de um dia, em ordem, e mantém a referência adaptativa."""

    def __init__(self, reference: Reference, cfg: PipelineConfig, seq: SequenceConfig):
        self.fixed = reference
        self.cfg = cfg
        self.seq = seq
        self.adaptive = reference.gray.astype(np.float32)  # estado: referência adaptativa (float)
        self.updates = np.zeros(len(reference.regions), int)  # nº de atualizações por vaga

    def adaptive_reference(self) -> Reference:
        gray = np.clip(self.adaptive + 0.5, 0, 255).astype(np.uint8)
        # a mediana só é usada pela compensação global de ganho (config. C da M2)
        median = float(np.median(gray)) if self.cfg.gain_compensation else self.fixed.median
        return Reference(gray=gray, median=median, regions=self.fixed.regions)

    def describe(self, gray: np.ndarray, keep_steps: bool = False,
                 fixed_result: FrameAnalysis | None = None) -> tuple[list[dict], dict]:
        """Descritores de cada vaga contra as referências ativas (sem atualizar o estado).

        `fixed_result` permite reaproveitar a análise contra a referência fixa, que não depende
        do estado (usado na busca em grade para não repetir o mesmo cálculo).
        """
        analyses = {}
        if self.seq.use_fixed:
            analyses["fix"] = fixed_result if fixed_result is not None else analyze(gray, self.fixed, self.cfg, keep_steps)
        if self.seq.use_adaptive:
            ref_ad = self.adaptive_reference()
            analyses["ad"] = analyze(gray, ref_ad, self.cfg, keep_steps)
        rows = []
        for i, region in enumerate(self.fixed.regions):
            any_rows = next(iter(analyses.values())).rows[i]
            row = {"space_id": region.id, **{k: any_rows[k] for k in FRAME_DESCRIPTORS}}
            for suffix, result in analyses.items():
                for k in REFERENCE_DESCRIPTORS:
                    row[f"{k}_{suffix}"] = result.rows[i][k]
            if "ad" in analyses:
                x, y, w, h = region.bbox
                row["ncc_ad"] = ncc(gray[y : y + h, x : x + w][region.mask], ref_ad.gray[y : y + h, x : x + w][region.mask])
            row["score"] = min(row[f"largest_frac_{s}"] for s in analyses)
            rows.append(row)
        steps = {s: a.steps for s, a in analyses.items()} if keep_steps else {}
        if keep_steps and "ad" in analyses:
            steps["reference_ad"] = ref_ad.gray
        return rows, steps

    def update(self, gray: np.ndarray, rows: list[dict]) -> None:
        """Atualização seletiva: só as vagas com escore < free_max entram na média móvel."""
        if not self.seq.use_adaptive:
            return
        a = self.seq.alpha
        for i, (region, row) in enumerate(zip(self.fixed.regions, rows)):
            if row["score"] < self.seq.free_max:
                x, y, w, h = region.bbox
                view = self.adaptive[y : y + h, x : x + w]
                view[region.mask] = (1 - a) * view[region.mask] + a * gray[y : y + h, x : x + w][region.mask]
                self.updates[i] += 1

    def step(self, gray: np.ndarray, keep_steps: bool = False,
             fixed_result: FrameAnalysis | None = None) -> tuple[list[dict], dict]:
        """Descreve o quadro e, em seguida, atualiza a referência adaptativa."""
        rows, steps = self.describe(gray, keep_steps, fixed_result)
        self.update(gray, rows)
        return rows, steps
