"""Casos de referência com imagens reais da amostra versionada (resultados conferidos na M2)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from parking.dataset import load_spaces, parse_frame  # noqa: E402
from parking.experiment import config_from, load_experiment, load_reference, read_image  # noqa: E402
from parking.pipeline import analyze, preprocess  # noqa: E402

M2 = load_experiment(ROOT / "configs/experimento_m2.json")
ENV = {**os.environ, "PYTHONUTF8": "1"}  # saída do processo filho em UTF-8 também no Windows


def classify(image: str) -> tuple[dict[int, int], dict[int, int | None]]:
    cfg = config_from(M2, "B_morfologia")
    frame = parse_frame(ROOT / image)
    reference = load_reference(M2["references"][frame.date], cfg)
    rows = analyze(preprocess(read_image(frame.path), cfg), reference, cfg).rows
    labels = {s.id: s.occupied for s in load_spaces(frame.xml_path)}
    return {r["space_id"]: r["predicted"] for r in rows}, labels


class TestCasosDeReferencia(unittest.TestCase):
    def test_nublado_10h_acerta_as_40_vagas(self):
        predicted, labels = classify("images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_10_00_04.jpg")
        self.assertEqual(sum(predicted.values()), 12)
        self.assertEqual(predicted, labels)

    def test_sol_baixo_erra_so_a_vaga_39(self):
        # falha conhecida (relatório M2, seção 6.2): carro escuro sobre asfalto na sombra
        predicted, labels = classify("images/input/UFPR05/Sunny/2013-14-16/2013-04-16_07_15_01.jpg")
        wrong = sorted(s for s in labels if predicted[s] != labels[s])
        self.assertEqual(wrong, [39])
        self.assertEqual((labels[39], predicted[39]), (1, 0))

    def test_run_pipeline_gera_as_saidas_esperadas(self):
        with tempfile.TemporaryDirectory() as tmp:
            done = subprocess.run(
                [sys.executable, str(ROOT / "src/run_pipeline.py"), "--image",
                 "images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_10_00_04.jpg", "--out", tmp],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=ENV)
            self.assertEqual(done.returncode, 0, done.stderr)
            out = Path(tmp) / "2013-04-14_10_00_04"
            for name in ("01_entrada.jpg", "05_limiarizada.png", "07_fechamento.png", "09_saida.jpg",
                         "painel.jpg", "vagas.csv", "resumo.json"):
                self.assertTrue((out / name).exists(), name)
            summary = json.loads((out / "resumo.json").read_text(encoding="utf-8"))
            self.assertEqual((summary["occupied"], summary["free"], summary["correct"]), (12, 28, 40))

    def test_imagem_inexistente_falha_com_mensagem(self):
        done = subprocess.run([sys.executable, str(ROOT / "src/run_pipeline.py"), "--image",
                               "images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_99_99_99.jpg"],
                              cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=ENV)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("Não foi possível ler a imagem", done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
