"""Indicadores calculados à mão em exemplos pequenos."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from parking.metrics import auc, classification_metrics, count_metrics, sweep_f1  # noqa: E402


class TestMetricas(unittest.TestCase):
    def test_matriz_de_confusao_e_indicadores(self):
        y = [1, 1, 1, 0, 0, 0, 0, 1]
        p = [1, 1, 0, 0, 0, 1, 0, 1]  # VP=3, FN=1, FP=1, VN=3
        m = classification_metrics(y, p)
        self.assertEqual((m["tp"], m["fp"], m["fn"], m["tn"]), (3, 1, 1, 3))
        self.assertAlmostEqual(m["precision"], 0.75)
        self.assertAlmostEqual(m["recall"], 0.75)
        self.assertAlmostEqual(m["specificity"], 0.75)
        self.assertAlmostEqual(m["f1"], 0.75)
        self.assertAlmostEqual(m["accuracy"], 0.75)

    def test_sem_positivos_previstos_precisao_indefinida(self):
        m = classification_metrics([0, 0, 1], [0, 0, 0])
        self.assertTrue(np.isnan(m["precision"]))
        self.assertEqual(m["f1"], 0.0)

    def test_erro_de_contagem(self):
        c = count_metrics(true_counts=[10, 20, 30], pred_counts=[12, 20, 27], n_spaces=40)
        self.assertAlmostEqual(c["count_mae"], 5 / 3)
        self.assertAlmostEqual(c["count_bias"], -1 / 3)
        self.assertEqual(c["count_max_abs"], 3)

    def test_auc(self):
        self.assertEqual(auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertEqual(auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)
        self.assertEqual(auc([0.5, 0.5], [0, 1]), 0.5)  # empate conta meio

    def test_sweep_f1_igual_ao_calculo_direto(self):
        rng = np.random.default_rng(0)
        scores, labels = rng.random(200), rng.random(200) < 0.4
        taus = np.linspace(0.05, 0.95, 19)
        for tau, f1 in zip(taus, sweep_f1(scores, labels, taus)):
            self.assertAlmostEqual(f1, classification_metrics(labels, scores >= tau)["f1"])


if __name__ == "__main__":
    unittest.main()
