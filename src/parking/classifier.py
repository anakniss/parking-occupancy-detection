"""Regressão logística com regularização L2, implementada em NumPy (M3).

Modelo: P(ocupada | x) = sigma(w0 + w . z), em que z = (x - média) / desvio é o vetor de
descritores padronizado com as estatísticas do conjunto de treino e sigma(t) = 1 / (1 + e^-t).

Treino: minimiza a entropia cruzada + (lam / 2) * ||w||^2 (o intercepto w0 não é penalizado)
pelo método de Newton (IRLS). A função é convexa, então o resultado é único e não depende
de inicialização aleatória: não há semente a fixar.

Escolhemos a regressão logística porque (1) os pesos sobre descritores padronizados mostram a
contribuição de cada descritor; (2) há poucos parâmetros para os poucos dias de treino;
(3) a saída é uma probabilidade, cujo limiar pode ser ajustado como o tau da regra.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


def _sigmoid(t: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(t, -50, 50)))


@dataclass
class LogisticModel:
    features: list[str]
    mean: np.ndarray
    std: np.ndarray
    weights: np.ndarray  # [w0, w1, ..., wk] sobre descritores padronizados
    threshold: float = 0.5
    lam: float = 1.0

    @classmethod
    def fit(cls, rows: list[dict], features: list[str], lam: float = 1.0, threshold: float = 0.5,
            max_iter: int = 100) -> LogisticModel:
        X = np.array([[r[f] for f in features] for r in rows], float)
        y = np.array([r["label"] for r in rows], float)
        mean, std = X.mean(0), X.std(0)
        std[std == 0] = 1.0
        Z = np.c_[np.ones(len(X)), (X - mean) / std]
        penalty = np.eye(Z.shape[1]) * lam
        penalty[0, 0] = 0.0
        w = np.zeros(Z.shape[1])
        for _ in range(max_iter):
            p = _sigmoid(Z @ w)
            grad = Z.T @ (p - y) + penalty @ w
            hess = Z.T @ (Z * (p * (1 - p))[:, None]) + penalty
            step = np.linalg.solve(hess, grad)
            w -= step
            if np.abs(step).max() < 1e-9:
                break
        return cls(list(features), mean, std, w, threshold, lam)

    def proba(self, rows: list[dict]) -> np.ndarray:
        X = np.array([[r[f] for f in self.features] for r in rows], float)
        return _sigmoid(self.weights[0] + ((X - self.mean) / self.std) @ self.weights[1:])

    def predict(self, rows: list[dict]) -> np.ndarray:
        return (self.proba(rows) >= self.threshold).astype(int)

    def to_dict(self) -> dict:
        return {
            "modelo": "regressão logística L2 (IRLS), descritores padronizados",
            "features": self.features,
            "mean": self.mean.tolist(),
            "std": self.std.tolist(),
            "intercept": float(self.weights[0]),
            "coefficients": dict(zip(self.features, self.weights[1:].tolist())),
            "threshold": self.threshold,
            "lam": self.lam,
        }

    def save(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> LogisticModel:
        weights = np.array([d["intercept"]] + [d["coefficients"][k] for k in d["features"]])
        return cls(d["features"], np.array(d["mean"]), np.array(d["std"]), weights, d["threshold"], d["lam"])

    @classmethod
    def load(cls, path: str | Path) -> LogisticModel:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
