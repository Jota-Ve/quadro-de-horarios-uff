
from pathlib import Path
from typing import Iterable

from lista_disciplinas import ListaDisciplinas


def extrai_disciplinas(lista_disc: Iterable[ListaDisciplinas]):
    """Extrai disciplinas de uma lista de ListaDisciplinas"""
    return {disc.codigo: disc.nome for lista in lista_disc for disc in lista.disciplinas}

def salva_discipllinas(disciplinas: dict[str, str], nome: Path|str):
    """Salva as disciplinas em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('CODIGO;NOME\n')
        for codigo, nome in disciplinas.items():
            f.write(f"{codigo};{nome}\n")


def extrai_turmas(lista_disc: Iterable[ListaDisciplinas]):
    """Extrai turmas de uma lista de ListaDisciplinas"""
    turmas: dict[int, tuple] = {}
    for lista in lista_disc:
        for disc in lista.disciplinas:
            ano, semestre = map(int, [disc.ano_semestre[:4], disc.ano_semestre[4]])
            turmas[disc._id] = (disc.turma, disc.tipo_de_oferta, disc.modulo, ano, semestre, disc.codigo, None)

    return turmas

def salva_turmas(turmas: dict[int, tuple], nome: Path|str):
    """Salva as turmas em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;TURMA;TIPO_DE_OFERTA;CARGA_HORARIA,ANO;SEMESTRE;DISCIPLINA;PROFESSOR\n')
        for id_, outras_colunas in turmas.items():
            f.write(f"{id_};" + ';'.join(map(str, outras_colunas)) + "\n")
