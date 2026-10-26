"""Indicadores de avaliação: classe positiva = vaga ocupada."""
from __future__ import annotations

import numpy as np


def _ratio(num: float, den: float) -> float:
    return num / den if den else float("nan")


def classification_metrics(y_true, y_pred) -> dict:
    """Matriz de confusão e indicadores por vaga."""
    y_true = np.asarray(y_true, bool)
    y_pred = np.asarray(y_pred, bool)
    tp = int((y_true & y_pred).sum())
    fp = int((~y_true & y_pred).sum())
    fn = int((y_true & ~y_pred).sum())
    tn = int((~y_true & ~y_pred).sum())
    recall = _ratio(tp, tp + fn)
    specificity = _ratio(tn, tn + fp)
    return {
        "n": int(y_true.size),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "accuracy": _ratio(tp + tn, y_true.size),
        "precision": _ratio(tp, tp + fp),
        "recall": recall,
        "specificity": specificity,
        "f1": _ratio(2 * tp, 2 * tp + fp + fn),
        "balanced_accuracy": float(np.nanmean([recall, specificity])),
    }


def count_metrics(true_counts, pred_counts, n_spaces: int) -> dict:
    """Erro na contagem de vagas ocupadas por imagem (o que um painel de ocupação exibiria)."""
    error = np.asarray(pred_counts, float) - np.asarray(true_counts, float)
    return {
        "frames": int(error.size),
        "count_mae": float(np.abs(error).mean()),
        "count_bias": float(error.mean()),
        "count_max_abs": float(np.abs(error).max()),
        "rate_mae_pp": float(np.abs(error).mean() / n_spaces * 100),
    }


def auc(scores, labels) -> float:
    """Área sob a curva ROC pela estatística de Mann-Whitney (empates contam meio)."""
    scores = np.asarray(scores, float)
    labels = np.asarray(labels, bool)
    pos, neg = scores[labels], scores[~labels]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    _, inverse, counts = np.unique(np.concatenate([pos, neg]), return_inverse=True, return_counts=True)
    mean_rank = np.cumsum(counts) - (counts - 1) / 2  # posto médio de cada valor (empates)
    ranks = mean_rank[inverse]
    u = ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2
    return float(u / (pos.size * neg.size))


def sweep_f1(scores, labels, thresholds) -> np.ndarray:
    """F1 para cada limiar de decisão (ocupada se score >= limiar)."""
    scores = np.asarray(scores, float)[None, :]
    labels = np.asarray(labels, bool)[None, :]
    pred = scores >= np.asarray(thresholds, float)[:, None]
    tp = (pred & labels).sum(1)
    fp = (pred & ~labels).sum(1)
    fn = (~pred & labels).sum(1)
    den = 2 * tp + fp + fn
    return np.where(den > 0, 2 * tp / np.maximum(den, 1), 0.0)
