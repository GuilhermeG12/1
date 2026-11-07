import unittest
from datetime import date
from pathlib import Path

from saude import DadosSamsung, respostas

PASTA = Path(__file__).resolve().parent.parent / "exemplo"
HOJE = date(2026, 11, 7)


class TestSaude(unittest.TestCase):
    def setUp(self):
        self.d = DadosSamsung(PASTA)

    def test_passos_semana_usa_total_de_aparelhos(self):
        self.assertEqual(self.d.passos_periodo(date(2026, 11, 2), HOJE), 26710)

    def test_resposta_passos_hoje(self):
        self.assertEqual(respostas.passos(self.d, "hoje", HOJE), "Você deu 3.210 passos hoje.")

    def test_ultima_frequencia_no_horario_local(self):
        r = self.d.ultima_frequencia()
        self.assertEqual((r["bpm"], r["quando"].hour, r["quando"].minute), (68, 11, 30))

    def test_ultima_atividade(self):
        a = self.d.ultima_atividade()
        self.assertEqual((a["tipo"], a["minutos"], a["distancia_km"]), ("Caminhada", 45, 3.5))

    def test_sono(self):
        self.assertEqual(self.d.ultimo_sono()["horas"], 7.5)


if __name__ == "__main__":
    unittest.main()
