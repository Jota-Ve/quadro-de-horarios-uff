import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.horario import Horario


def map_tupla_para_horarios(HHMM_HHMM: tuple[int, int, int, int]) -> str:
    """Converte uma tupla de 4 inteiros (HH, MM, HH, MM) em uma string no formato HH:MM-HH:MM"""
    return f"{HHMM_HHMM[0]:02d}:{HHMM_HHMM[1]:02d}-{HHMM_HHMM[2]:02d}:{HHMM_HHMM[3]:02d}"


class TestHorario:

    # estratégia que gera qualquer intervalo HH:MM-HH:MM
    horarios = st.tuples(
        st.integers(0, 23), st.integers(0, 59),
        st.integers(0, 23), st.integers(0, 59),
    ).map(map_tupla_para_horarios)

    horarios_8h_as_10h59 = st.tuples(
        st.integers(8, 9), st.integers(0, 59),  # início candidato entre 08:00 e 09:59
        st.integers(8, 10), st.integers(0, 59), # fim candidato entre 08:00 e 10:59
    ).map(map_tupla_para_horarios)


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
            assert pytest.raises(ValueError, lambda: Horario(horario))


    @given(horarios_8h_as_10h59)
    def test_contem_entre_8h_e_10h59(self, horario: str):
        print('horario gerado:', horario)
        if Horario.valido(horario):
            _8h_as_10h = Horario("08:00-10:00")
            inicio, fim = horario.split("-")
            inicio_hh, inicio_mm = map(int, inicio.split(":"))
            fim_hh, fim_mm       = map(int, fim.split(":"))

            if (horario in _8h_as_10h):
                assert (inicio_hh, inicio_mm) >= (8, 0)
                assert (fim_hh,    fim_mm)    <= (10, 0)
            else:
                assert (inicio_hh, inicio_mm) < (8, 0) or (10, 0) < (fim_hh, fim_mm)
