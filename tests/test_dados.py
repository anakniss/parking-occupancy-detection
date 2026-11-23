"""Leitura das entradas: nomes de arquivo, XML do PKLot e conversão das anotações do Hugging Face."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from get_data import iter_samples, to_xml  # noqa: E402
from parking.dataset import list_frames, load_spaces, parse_frame  # noqa: E402

SAMPLE = ROOT / "images/input/UFPR05/Cloudy/2013-04-14/2013-04-14_10_00_04.jpg"


class TestNomesEXml(unittest.TestCase):
    def test_data_vem_do_nome_do_arquivo_e_nao_da_pasta(self):
        # a pasta do dia ensolarado da amostra está nomeada 2013-14-16
        frame = parse_frame(ROOT / "images/input/UFPR05/Sunny/2013-14-16/2013-04-16_07_15_01.jpg")
        self.assertEqual((frame.date, frame.time, frame.condition), ("2013-04-16", "07:15:01", "Sunny"))

    def test_nome_fora_do_padrao_e_rejeitado(self):
        with self.assertRaises(ValueError):
            parse_frame("images/input/UFPR05/Sunny/2013-04-16/foto.jpg")

    def test_xml_tem_40_vagas_com_poligono_e_rotulo(self):
        spaces = load_spaces(SAMPLE.with_suffix(".xml"))
        self.assertEqual([s.id for s in spaces], list(range(1, 41)))
        self.assertTrue(all(s.contour.shape == (4, 2) for s in spaces))
        self.assertEqual(sum(s.occupied for s in spaces), 12)  # conferido no painel da M2

    def test_vaga_sem_rotulo_vira_none(self):
        spaces = {s.id: s for s in load_spaces(ROOT / "images/input/UFPR05/Sunny/2013-14-16/2013-04-16_07_25_01.xml")}
        self.assertIsNone(spaces[15].occupied)

    def test_amostra_versionada_tem_140_imagens_com_xml(self):
        frames = [f for f in list_frames(ROOT / "images/input/UFPR05")
                  if f.path.parent.name in ("2013-04-14", "2013-14-16", "2013-04-13")
                  and f.path.parent.parent.name in ("Cloudy", "Sunny", "Rainy")
                  and f"{f.path.parent.parent.name}/{f.path.parent.name}" in
                  ("Cloudy/2013-04-14", "Sunny/2013-14-16", "Rainy/2013-04-13")]
        self.assertEqual(len(frames), 140)
        self.assertTrue(all(f.xml_path.exists() for f in frames))


class TestConversaoHuggingFace(unittest.TestCase):
    def test_to_xml_preserva_ids_pontos_e_rotulos(self):
        sample = {
            "source": "ufpr05",
            "parking_spaces": {"polylines": [
                {"space_id": 2, "occupancy_status": "occupied", "points": [[[0.5, 0.5], [0.25, 0.75]]]},
                {"space_id": 1, "occupancy_status": "not occupied", "points": [[[0.1, 0.2], [0.3, 0.4]]]},
                {"space_id": 3, "occupancy_status": "unknown", "points": [[[0.0, 0.0], [1.0, 1.0]]]},
            ]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.xml"
            path.write_text(to_xml(sample), encoding="utf-8")
            spaces = load_spaces(path)
        self.assertEqual([s.id for s in spaces], [1, 2, 3])
        self.assertEqual([s.occupied for s in spaces], [0, 1, None])
        self.assertEqual(spaces[1].contour.tolist(), [[640, 360], [320, 540]])
        self.assertEqual(spaces[2].contour.tolist(), [[0, 0], [1280, 720]])

    @unittest.skipUnless(os.environ.get("VERIFICAR_CONVERSAO") == "1",
                         "lento (lê o samples.json de 267 MB); rode com VERIFICAR_CONVERSAO=1")
    def test_conversao_reproduz_os_140_xml_originais(self):
        cache = sorted((ROOT / ".cache/pklot").glob("samples_*.json"))
        if not cache:
            self.skipTest("samples.json ainda não baixado (python src/get_data.py)")
        index = {Path(s["filepath"]).stem: s for s in iter_samples(cache[0]) if s["source"] == "ufpr05"}
        versioned = ("Cloudy/2013-04-14", "Sunny/2013-14-16", "Rainy/2013-04-13")
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            for folder in versioned:
                for xml in sorted((ROOT / "images/input/UFPR05" / folder).glob("*.xml")):
                    converted = Path(tmp) / xml.name
                    converted.write_text(to_xml(index[xml.stem]), encoding="utf-8")
                    for a, b in zip(load_spaces(xml), load_spaces(converted), strict=True):
                        self.assertEqual((a.id, a.occupied, a.contour.tolist()), (b.id, b.occupied, b.contour.tolist()))
                    checked += 1
        self.assertEqual(checked, 140)


if __name__ == "__main__":
    unittest.main()
