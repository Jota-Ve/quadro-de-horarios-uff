import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.horario import Horario


class TestHorario:

    # estratégia que gera qualquer intervalo HH:MM-HH:MM
    horarios = st.tuples(
        st.integers(0, 23), st.integers(0, 59),
        st.integers(0, 23), st.integers(0, 59),
    ).map(lambda hh_mm: f"{hh_mm[0]:02d}:{hh_mm[1]:02d}-{hh_mm[2]:02d}:{hh_mm[3]:02d}")


    @pytest.mark.parametrize("horario", [
        "08:00-10:00",
        "00:00-23:59",
        "23:58-23:59",
        "12:30-13:45",
        "17:59-18:00",
    ])
    def test_validar_horario_valido_deve_passar(self, horario: str):
        assert Horario.valido(horario)

    @given(horarios)
    def test_validar_horario_com_inicio_antes_do_fim_deve_passar(self, horario: str):
        inicio, fim = horario.split("-")
        if inicio < fim:
            assert Horario.valido(horario)

    @pytest.mark.parametrize("horario", [
        "08:00-08:00",
        "09:00-09:00",
        "13:49-13:49",
        "00:00-00:00",
        "22:00-22:00",
    ])
    def test_validar_horario_com_inicio_e_fim_iguais_deve_falhar(self, horario: str):
        assert not Horario.valido(horario)

    @given(horarios)
    def test_validar_horario_com_inicio_depois_do_fim_deve_falhar(self, horario: str):
        inicio, fim = horario.split("-")
        if inicio > fim:
            assert not Horario.valido(horario)

    @pytest.mark.parametrize("horario", [
        "8:00-10:00",
        "08:00-10:0",
        "08:00/10:00",
        "08:00_10:00",
        "08001000",
        "           ",
        " ",
        "",
        "\n",
        "08:00-10:00 ",
        " 08:00-10:00",
        " 08:00-10:00 ",
    ])
    def test_validar_formato_diferente_de_HHMM_HHMM_deve_falhar(self, horario: str):
        assert not Horario.valido(horario)


    @given(horarios)
    def test_instanciar_horario_valido_deve_passar(self, horario: str):
        if Horario.valido(horario):
            # propriedade observável: instanciar não deve lançar erro
            h = Horario(horario)
            assert isinstance(h, Horario)

    @given(horarios)
    def test_instanciar_horario_invalido_deve_falhar(self, horario: str):
        if not Horario.valido(horario):
            # propriedade observável: se inválido, instanciar falha
            assert pytest.raises(ValueError, lambda: Horario(horario))


    def test_contem(self):
        h = Horario("08:00-10:00")
        assert "08:30-09:30" in h
        assert "07:30-09:30" not in h
        assert "08:30-10:30" not in h