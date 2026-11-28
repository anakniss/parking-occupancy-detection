"""Pipeline, referência adaptativa e classificador em cenas sintéticas com resposta conhecida."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from parking.classifier import LogisticModel  # noqa: E402
from parking.dataset import Space  # noqa: E402
from parking.pipeline import PipelineConfig, analyze, apply_morphology, build_regions, Reference  # noqa: E402
from parking.sequence import DayProcessor, SequenceConfig, ncc  # noqa: E402

CFG = PipelineConfig(blur_ksize=1, diff_threshold=25, open_ksize=3, close_ksize=7, min_component_area=15,
                     occupancy_threshold=0.24)
H, W = 120, 200
# duas vagas retangulares lado a lado
SPACES = [
    Space(1, 0, np.array([[10, 20], [90, 20], [90, 100], [10, 100]], np.int32)),
    Space(2, 0, np.array([[110, 20], [190, 20], [190, 100], [110, 100]], np.int32)),
]


def asphalt(seed: int = 0, level: int = 90) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.clip(level + rng.normal(0, 4, (H, W)), 0, 255).astype(np.uint8)


def reference(gray: np.ndarray) -> Reference:
    return Reference(gray=gray, median=float(np.median(gray)), regions=build_regions(SPACES, gray.shape))


def with_car(gray: np.ndarray, x0: int = 20, level: int = 200) -> np.ndarray:
    out = gray.copy()
    out[35:85, x0:x0 + 60] = level
    out[45:60, x0 + 10:x0 + 50] = 40  # para-brisa escuro: o carro não é uniforme
    return out


class TestPipeline(unittest.TestCase):
    def test_carro_ocupa_so_a_sua_vaga(self):
        ref = asphalt(0)
        rows = analyze(with_car(asphalt(1)), reference(ref), CFG).rows
        self.assertEqual([r["predicted"] for r in rows], [1, 0])
        self.assertGreater(rows[0]["largest_frac"], 0.4)

    def test_ruido_do_sensor_nao_ocupa_vaga(self):
        rows = analyze(asphalt(1), reference(asphalt(0)), CFG).rows
        self.assertEqual([r["predicted"] for r in rows], [0, 0])

    def test_abertura_remove_pontos_isolados_e_fechamento_une_fragmentos(self):
        mask = np.zeros((60, 60), np.uint8)
        mask[5, 5] = mask[50, 10] = 255  # pontos isolados
        mask[20:40, 20:29] = mask[20:40, 32:41] = 255  # dois fragmentos separados por 3 px
        opened, closed = apply_morphology(mask, 3, 7)
        self.assertEqual(opened[5, 5], 0)
        self.assertEqual(opened[50, 10], 0)
        self.assertEqual(closed[30, 30], 255)  # lacuna preenchida

    def test_ncc_invariante_a_ganho_e_deslocamento(self):
        a = asphalt(3).astype(float)
        self.assertAlmostEqual(ncc(a, 1.4 * a + 20), 1.0, places=6)
        self.assertAlmostEqual(ncc(a, -a), -1.0, places=6)


class TestReferenciaAdaptativa(unittest.TestCase):
    def test_deriva_de_iluminacao_e_absorvida_nas_vagas_livres(self):
        ref = asphalt(0, level=90)
        fixed = DayProcessor(reference(ref), CFG, SequenceConfig(use_fixed=True, use_adaptive=False))
        adaptive = DayProcessor(reference(ref), CFG, SequenceConfig(use_fixed=False, use_adaptive=True, alpha=0.5,
                                                                     free_max=0.12))
        # o asfalto clareia 5 níveis por quadro (sol subindo): 90 -> 150 em 12 quadros
        for t in range(1, 13):
            frame = asphalt(t, level=90 + 5 * t)
            rows_fixed, _ = fixed.step(frame)
            rows_adaptive, _ = adaptive.step(frame)
        self.assertEqual([r["score"] >= 0.24 for r in rows_fixed], [True, True])  # referência fixa: falsos positivos
        self.assertEqual([r["score"] >= 0.24 for r in rows_adaptive], [False, False])

    def test_veiculo_parado_nao_e_incorporado_a_referencia(self):
        proc = DayProcessor(reference(asphalt(0)), CFG, SequenceConfig(use_fixed=True, use_adaptive=True, alpha=1.0,
                                                                        free_max=0.2))
        for t in range(1, 30):
            rows, _ = proc.step(with_car(asphalt(t)))
            self.assertGreaterEqual(rows[0]["score"], 0.24, f"quadro {t}")
        self.assertEqual(proc.updates.tolist(), [0, 29])  # só a vaga livre foi atualizada

    def test_dupla_exige_diferenca_das_duas_referencias(self):
        proc = DayProcessor(reference(asphalt(0)), CFG, SequenceConfig(alpha=0.5, free_max=0.2))
        rows, _ = proc.describe(with_car(asphalt(1)))
        self.assertEqual(rows[0]["score"], min(rows[0]["largest_frac_fix"], rows[0]["largest_frac_ad"]))

    def test_pelo_menos_uma_referencia(self):
        with self.assertRaises(ValueError):
            SequenceConfig(use_fixed=False, use_adaptive=False)


class TestTexturaLBP(unittest.TestCase):
    def test_codigos_lbp_uniformes(self):
        from explore_dev import lbp_riu2

        flat = np.full((5, 5), 100, np.uint8)
        self.assertTrue((lbp_riu2(flat)[1:-1, 1:-1] == 8).all())  # todos os vizinhos >= centro
        peak = flat.copy()
        peak[2, 2] = 200
        self.assertEqual(lbp_riu2(peak)[2, 2], 0)  # centro mais claro que todos os vizinhos
        edge = flat.copy()
        edge[:, 3:] = 200  # borda vertical entre as colunas 2 e 3
        self.assertEqual(lbp_riu2(edge)[2, 2], 8)  # centro 100: todos os vizinhos (100 ou 200) >= centro
        # centro 200 na coluna 3: vizinhos >= 200 são os 2 da mesma coluna e os 3 da coluna 4 (padrão uniforme)
        self.assertEqual(lbp_riu2(edge)[2, 3], 5)
        self.assertEqual(lbp_riu2(flat)[0, 0], 255)  # borda sem código


class TestClassificador(unittest.TestCase):
    def test_separa_classes_e_salva_sem_perder_precisao(self):
        rng = np.random.default_rng(1)
        rows = [{"a": rng.normal(2 * y, 0.5), "b": rng.normal(0, 1), "label": y} for y in rng.integers(0, 2, 400)]
        model = LogisticModel.fit(rows, ["a", "b"], lam=1.0)
        accuracy = np.mean(model.predict(rows) == np.array([r["label"] for r in rows]))
        self.assertGreater(accuracy, 0.95)
        self.assertGreater(model.weights[1], 0)  # 'a' maior -> ocupada
        self.assertLess(abs(model.weights[2]), abs(model.weights[1]) / 5)  # 'b' é ruído
        with tempfile.TemporaryDirectory() as tmp:
            model.save(Path(tmp) / "m.json")
            loaded = LogisticModel.load(Path(tmp) / "m.json")
        np.testing.assert_allclose(loaded.proba(rows), model.proba(rows))

    def test_treino_e_deterministico(self):
        rows = [{"a": float(i % 7), "label": int(i % 7 > 3)} for i in range(100)]
        w1 = LogisticModel.fit(rows, ["a"]).weights
        w2 = LogisticModel.fit(rows, ["a"]).weights
        np.testing.assert_array_equal(w1, w2)


if __name__ == "__main__":
    unittest.main()
