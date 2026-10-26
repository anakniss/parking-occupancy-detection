"""Figuras das saídas intermediárias e dos experimentos."""
from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .pipeline import SpaceRegion  # noqa: E402

# Paleta (hex) — séries em ordem fixa; estados livre/ocupada/erro com cores de status.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
FREE, OCCUPIED, ERROR = "#0ca30c", "#d03b3b", "#fab219"


def _bgr(hex_color: str) -> tuple[int, int, int]:
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return b, g, r


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 10,
            "text.color": INK,
            "axes.labelcolor": INK_2,
            "axes.edgecolor": AXIS,
            "axes.titlecolor": INK,
            "axes.titlesize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK_2,
            "ytick.labelcolor": INK_2,
            "legend.frameon": False,
            "lines.linewidth": 2,
        }
    )


# ---------------------------------------------------------------- imagens (OpenCV)


def _label(img: np.ndarray, text: str, org: tuple[int, int], scale: float = 0.45) -> None:
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA)


def draw_spaces(bgr: np.ndarray, regions: list[SpaceRegion], color: str = "#ffffff") -> np.ndarray:
    """Contorno e id de cada vaga (mapa de vagas conhecido)."""
    out = bgr.copy()
    for region in regions:
        cv2.polylines(out, [region.contour], True, _bgr(color), 1, cv2.LINE_AA)
        cx, cy = region.contour.mean(0).astype(int)
        _label(out, str(region.id), (cx - 7, cy + 5), 0.4)
    return out


def draw_result(
    bgr: np.ndarray,
    regions: list[SpaceRegion],
    rows: list[dict],
    labels: dict[int, int] | None = None,
    summary: list[str] | None = None,
) -> np.ndarray:
    """Saída final: vagas livres em verde, ocupadas em vermelho; erros (FP/FN) em amarelo."""
    out = bgr.copy()
    overlay = bgr.copy()
    by_id = {row["space_id"]: row for row in rows}
    for region in regions:
        predicted = by_id[region.id]["predicted"]
        color = OCCUPIED if predicted else FREE
        cv2.fillPoly(overlay, [region.contour], _bgr(color))
    out = cv2.addWeighted(overlay, 0.30, out, 0.70, 0)
    for region in regions:
        predicted = by_id[region.id]["predicted"]
        cv2.polylines(out, [region.contour], True, _bgr(OCCUPIED if predicted else FREE), 2, cv2.LINE_AA)
        cx, cy = region.contour.mean(0).astype(int)
        text = str(region.id)
        if labels is not None and labels.get(region.id) is not None and labels[region.id] != predicted:
            cv2.polylines(out, [region.contour], True, _bgr(ERROR), 4, cv2.LINE_AA)
            text += " FP" if predicted else " FN"
        _label(out, text, (cx - 10, cy + 5))
    if summary:
        height = 22 * len(summary) + 12
        box = out[0:height, 0:430].copy()
        out[0:height, 0:430] = cv2.addWeighted(box, 0.35, np.zeros_like(box), 0.65, 0)
        for i, line in enumerate(summary):
            cv2.putText(out, line, (10, 24 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def diff_view(diff: np.ndarray, vmax: int = 100) -> np.ndarray:
    """Mapa de calor da diferença absoluta; escala fixa 0..vmax para comparar quadros."""
    scaled = np.clip(diff.astype(np.float32) * (255.0 / vmax), 0, 255).astype(np.uint8)
    return cv2.applyColorMap(scaled, cv2.COLORMAP_INFERNO)


def mask_view(mask: np.ndarray, regions: list[SpaceRegion]) -> np.ndarray:
    out = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    for region in regions:
        cv2.polylines(out, [region.contour], True, _bgr(SERIES[0]), 1, cv2.LINE_AA)
    return out


def components_view(components: np.ndarray, regions: list[SpaceRegion], rows: list[dict]) -> np.ndarray:
    """Componentes conexos com cores aleatórias; o maior componente de cada vaga recebe contorno."""
    rng = np.random.default_rng(7)
    palette = rng.integers(60, 256, size=(int(components.max()) + 1, 3), dtype=np.uint8)
    palette[0] = 0
    out = palette[components]
    for region in regions:
        cv2.polylines(out, [region.contour], True, (150, 150, 150), 1, cv2.LINE_AA)
    by_id = {row["space_id"]: row for row in rows}
    for region in regions:
        cx, cy = region.contour.mean(0).astype(int)
        _label(out, f"{by_id[region.id]['largest_frac']:.2f}", (cx - 14, cy + 5), 0.38)
    return out


# ---------------------------------------------------------------- figuras (Matplotlib)


def _rgb(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) if bgr.ndim == 3 else bgr


def save_panel(images: list[tuple[str, np.ndarray]], path: Path, cols: int = 3) -> None:
    style()
    rows = int(np.ceil(len(images) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 3.2 * rows))
    for ax in np.ravel(axes):
        ax.axis("off")
    for ax, (title, img) in zip(np.ravel(axes), images):
        ax.imshow(_rgb(img), cmap="gray" if img.ndim == 2 else None, vmin=0, vmax=255)
        ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=120, pil_kwargs={"quality": 88})
    plt.close(fig)


def plot_tuning(curves: dict[str, tuple[list, list]], chosen: dict[str, int], path: Path) -> None:
    style()
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for color, (name, (thresholds, f1)) in zip(SERIES, curves.items()):
        ax.plot(thresholds, f1, color=color, marker="o", markersize=5, label=name)
        best = thresholds.index(chosen[name])
        ax.plot([chosen[name]], [f1[best]], marker="o", markersize=10, color=color, mec=SURFACE, mew=2)
    ax.set_xlabel("Limiar da diferença T (níveis de cinza)")
    ax.set_ylabel("Melhor F1 no dia de ajuste")
    ax.set_title("Ajuste de T (ponto grande = valor escolhido)", loc="left")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_counts(days: list[dict], configs: list[str], path: Path) -> None:
    """Uma linha do tempo por dia: vagas ocupadas pelo rótulo e por cada configuração."""
    style()
    fig, axes = plt.subplots(len(days), 1, figsize=(9, 2.7 * len(days)), sharey=True)
    for ax, day in zip(np.atleast_1d(axes), days):
        x = np.arange(len(day["times"]))
        ax.plot(x, day["true"], color=INK, linewidth=3, label="Rótulo (XML)")
        for color, name in zip(SERIES, configs):
            ax.plot(x, day[name], color=color, label=name)
        step = max(1, len(x) // 10)
        ax.set_xticks(x[::step], [t[:5] for t in day["times"][::step]])
        ax.set_ylim(-1, 42)
        ax.set_ylabel("Vagas ocupadas")
        ax.set_title(day["title"], loc="left")
    np.atleast_1d(axes)[0].legend(loc="upper left", ncol=4)
    np.atleast_1d(axes)[-1].set_xlabel("Horário da captura")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_score_histograms(panels: list[dict], path: Path) -> None:
    """Distribuição do descritor de decisão (fração do maior componente) por classe."""
    style()
    fig, axes = plt.subplots(1, len(panels), figsize=(4.2 * len(panels), 3.3), sharey=True)
    bins = np.linspace(0, 1, 41)
    for ax, panel in zip(np.atleast_1d(axes), panels):
        scores, labels = np.asarray(panel["scores"]), np.asarray(panel["labels"], bool)
        ax.hist(scores[~labels], bins=bins, density=True, color=SERIES[0], alpha=0.75, label="livre")
        ax.hist(scores[labels], bins=bins, density=True, color=SERIES[1], alpha=0.75, label="ocupada")
        ax.axvline(panel["tau"], color=INK, linestyle="--", linewidth=1.5)
        tau_text = f"τ = {panel['tau']:.2f}".replace(".", ",")
        ax.text(panel["tau"] + 0.02, 0.95, tau_text, transform=ax.get_xaxis_transform(), color=INK_2)
        ax.set_title(panel["title"], loc="left", fontsize=10)
        ax.set_xlabel("Fração da vaga no maior componente")
        ax.set_yscale("log")
    np.atleast_1d(axes)[0].set_ylabel("Densidade (escala log)")
    np.atleast_1d(axes)[0].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_errors_by_space(fp: np.ndarray, fn: np.ndarray, space_ids: list[int], title: str, path: Path) -> None:
    style()
    fig, ax = plt.subplots(figsize=(10, 3.2))
    x = np.arange(len(space_ids))
    ax.bar(x, fp, color=SERIES[0], width=0.8, label="Falso positivo (livre → ocupada)")
    ax.bar(x, fn, bottom=fp, color=SERIES[1], width=0.8, label="Falso negativo (ocupada → livre)")
    ax.set_xticks(x, space_ids, fontsize=8)
    ax.set_xlabel("Id da vaga")
    ax.set_ylabel("Erros (quadros)")
    ax.set_title(title, loc="left")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_cases(cases: list[dict], path: Path) -> None:
    """Uma linha por caso: referência, atual, diferença, binária, morfologia, componentes."""
    style()
    columns = ["Referência", "Atual", "Diferença", "Limiarizada", "Após morfologia", "Componentes"]
    fig, axes = plt.subplots(len(cases), len(columns), figsize=(2.1 * len(columns), 2.0 * len(cases) + 0.4))
    axes = np.atleast_2d(axes)
    for r, case in enumerate(cases):
        for c, key in enumerate(["reference", "current", "diff", "binary", "closed", "components"]):
            ax = axes[r, c]
            img = case["crops"][key]
            ax.imshow(_rgb(img), cmap="gray" if img.ndim == 2 else None, vmin=0, vmax=255)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            for spine in ax.spines.values():
                spine.set_visible(False)
            if r == 0:
                ax.set_title(columns[c], fontsize=9)
        axes[r, 0].set_ylabel(case["title"], fontsize=8, rotation=0, ha="right", va="center", labelpad=6)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
