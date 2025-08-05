
from pathlib import Path
from typing import Iterable

import horario
from lista_disciplinas import ListaDisciplinas


def extrai_disciplinas(lista_disc: Iterable[ListaDisciplinas]):
    """Extrai disciplinas de uma lista de ListaDisciplinas"""
    return {disc.codigo: disc.nome for lista in lista_disc for disc in lista.disciplinas}

def salva_discipllinas(disciplinas: dict[str, str], nome: Path|str) -> None:
    """Salva as disciplinas em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('CODIGO;NOME\n')
        for codigo, nome in sorted(disciplinas.items()):
            f.write(f"{codigo};{nome}\n")


def extrai_turmas(lista_disc: Iterable[ListaDisciplinas]):
    """Extrai turmas de uma lista de ListaDisciplinas"""
    turmas: dict[int, tuple] = {}
    for lista in lista_disc:
        for disc in lista.disciplinas:
            ano, semestre = map(int, [disc.ano_semestre[:4], disc.ano_semestre[4]])
            turmas[disc._id] = (disc.turma, disc.tipo_de_oferta, disc.modulo, ano, semestre, disc.codigo, None)

    return turmas

def salva_turmas(turmas: dict[int, tuple], nome: Path|str) -> None:
    """Salva as turmas em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;TURMA;TIPO_DE_OFERTA;CARGA_HORARIA,ANO;SEMESTRE;DISCIPLINA;PROFESSOR\n')
        for id_, outras_colunas in sorted(turmas.items()):
            f.write(f"{id_};" + ';'.join(map(str, outras_colunas)) + "\n")


def salva_cursos(cursos: dict[int, str], nome: Path|str) -> None:
    """Salva os cursos em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;NOME\n')
        for id_, nome in sorted(cursos.items()):
            f.write(f"{id_};{nome}\n")


_ExtracaoHorarios = set[tuple[horario.DiaDaSemana, str, str]]
def extrai_horarios(lista_disc: Iterable[ListaDisciplinas]) -> _ExtracaoHorarios:
    """Extrai horários de uma lista de ListaDisciplinas"""
    horarios: _ExtracaoHorarios = set()
    for lista in lista_disc:
        for disc in lista.disciplinas:
            for dia, horarios_no_dia in disc.horario.items():
                horarios.update((dia, horario.inicio, horario.fim) for horario in horarios_no_dia)

    return horarios

def salva_horarios(horarios: _ExtracaoHorarios, nome: Path|str) -> None:
    """Salva os horários em um arquivo CSV"""
    def ordena_semana(dia: horario.DiaDaSemana) -> int:
        return {horario.DiaDaSemana.SEGUNDA: 0,
                horario.DiaDaSemana.TERCA: 1,
                horario.DiaDaSemana.QUARTA: 2,
                horario.DiaDaSemana.QUINTA: 3,
                horario.DiaDaSemana.SEXTA: 4,
                horario.DiaDaSemana.SABADO: 5}[dia]

    with open(nome, 'w', encoding='utf-8') as f:
        f.write('DIA;INICIO;FIM\n')
        for dia, inicio, fim in sorted(horarios, key=lambda items: (ordena_semana(items[0]), items[1:])):
            f.write(f"{dia.name};{inicio};{fim}\n")