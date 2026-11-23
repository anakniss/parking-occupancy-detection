"""Casos de referência com imagens reais da amostra versionada (resultados conferidos na M2)."""
from __future__ import annotations

import csv
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


def run_day(tmp: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "src/run_day.py"), "--dia", "2013-04-16", "--out", tmp, *extra],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=ENV)


def row_at(csv_path: Path, hhmm: str) -> dict:
    with open(csv_path, encoding="utf-8") as f:
        return next(r for r in csv.DictReader(f) if r["horario"].startswith(hhmm))


class TestRunDay(unittest.TestCase):
    """O dia 2013-04-16 está todo na amostra versionada: estes testes rodam sem internet."""

    def test_baseline_reproduz_a_m2(self):
        # B da M2 em 16/04: VP 1744 + VN 320 = 2064 acertos (images/results/experimentos/metricas.csv)
        with tempfile.TemporaryDirectory() as tmp:
            done = run_day(tmp, "--variante", "B_M2", "--quadro", "07:15")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("2064/2079", done.stdout)
            out = Path(tmp) / "2013-04-16_B_M2"
            r = row_at(out / "ocupacao.csv", "07:15")
            self.assertEqual((r["ocupadas"], r["acertos"]), ("22", "39"))  # igual ao run_pipeline.py
            self.assertTrue((out / "painel_0715.jpg").exists())

    def test_sistema_final_no_dia_de_desenvolvimento(self):
        # dupla em 16/04: 6 FP + 12 FN (images/results/m3/desenvolvimento/metricas_desenvolvimento.csv)
        with tempfile.TemporaryDirectory() as tmp:
            done = run_day(tmp)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("2061/2079", done.stdout)
            self.assertTrue((Path(tmp) / "2013-04-16" / "ocupacao.csv").exists())

    def test_variante_inexistente_falha_com_as_opcoes(self):
        with tempfile.TemporaryDirectory() as tmp:
            done = run_day(tmp, "--variante", "X")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("B_M2", done.stdout + done.stderr)


class TestSeparacaoDasDivisoes(unittest.TestCase):
    def test_desenvolvimento_nao_lista_os_dias_de_teste(self):
        from run_final import Dataset

        experiment = load_experiment(ROOT / "configs/experimento_m3.json")
        # só as pastas versionadas no desenvolvimento e uma pasta de teste que não existe
        experiment["splits"] = {"desenvolvimento": ["Cloudy/2013-04-14", "Sunny/2013-14-16", "Rainy/2013-04-13"],
                                "teste": ["Cloudy/1999-01-01"]}
        data = Dataset(experiment, ["desenvolvimento"])  # não falha: o teste nem é listado
        self.assertEqual(list(data.frames), ["desenvolvimento"])
        self.assertEqual(len(data.manifest()), 140)
        with self.assertRaises(SystemExit):
            Dataset(experiment)  # carregando o teste, a pasta inexistente é detectada


if __name__ == "__main__":
    unittest.main()
