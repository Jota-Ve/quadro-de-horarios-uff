from src.horario import Horario
import pytest

class TestHorario:

    # @pytest.p
    def test_valido_passa(self):
        assert Horario.valido("08:00-10:00")

    def test_valido_inicio_e_fim_iguais_falha(self):
        assert not Horario.valido("08:00-08:00")

    def test_valido_inicio_maior_que_fim_falha(self):
        assert not Horario.valido("10:00-08:00")

    def test_valido_formato_HMM_HHMM_falha(self):
        assert not Horario.valido("8:00-10:00")

    def test_valido_formato_HHMM_HMM_falha(self):
        assert not Horario.valido("08:00-10:0")

    def test_valido_formato_separador_incorreto_falha(self):
        assert not Horario.valido("08:00/10:00")

    def test_contem(self):
        h = Horario("08:00-10:00")
        assert "08:30-09:30" in h
        assert "07:30-09:30" not in h
        assert "08:30-10:30" not in h