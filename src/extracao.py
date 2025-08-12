
from pathlib import Path
from typing import Iterable

import curso
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
        f.write('ID;TURMA;TIPO_DE_OFERTA;CARGA_HORARIA;ANO;SEMESTRE;DISCIPLINA;PROFESSOR\n')
        for id_, outras_colunas in sorted(turmas.items()):
            f.write(f"{id_};" + ';'.join(map(lambda x: 'NULL' if x in {None, '-'} else str(x), outras_colunas)) + "\n")


def salva_cursos(cursos: set[curso.Curso], nome: Path|str) -> None:
    """Salva os cursos em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;NOME\n')
        for _curso in sorted(cursos, key=lambda x: x.id):
            f.write(f"{_curso.id};{_curso.nome}\n")


def salva_vagas(vagas: dict[int, dict[curso.Curso, dict[str, int]]], nome: Path|str) -> None:
    """Salva as vagas em um arquivo CSV"""
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('TURMA_ID;CURSO_ID;VAGAS_REGULAR;VAGAS_VESTIBULAR;INSCRITOS_REGULAR;INSCRITOS_VESTIBULAR;EXCEDENTES;CANDIDATOS\n')
        for turma_id, cursos in sorted(vagas.items()):
            for _curso, info in cursos.items():
                f.write(f"{turma_id};{_curso.id};{info.get('vagas_regular', 0)};{info.get('vagas_vestibular', 0)};"
                        f"{info.get('inscritos_regular', 0)};{info.get('inscritos_vestibular', 0)};"
                        f"{info.get('excedentes', 0)};{info.get('candidatos', 0)}\n")


_ExtracaoHorarios = dict[tuple[horario.DiaDaSemana, str, str], set[int]]
def extrai_horarios_e_turmas(lista_disc: Iterable[ListaDisciplinas]) -> _ExtracaoHorarios:
    """Extrai horários de uma lista de ListaDisciplinas e os IDs das turmas que os ocupam.

    Retorna um dicionário onde as chaves são tuplas (dia_da_semana, hora_inicio, hora_fim)
    e os valores são conjuntos de IDs das turmas que ocupam aquele horário.
    """
    horarios: _ExtracaoHorarios = dict()
    for lista in lista_disc:
        for disc in lista.disciplinas:
            for dia, horarios_no_dia in disc.horario.items():
                for disc_hr in horarios_no_dia:
                    if (dia, disc_hr.inicio, disc_hr.fim) not in horarios:
                        horarios[(dia, disc_hr.inicio, disc_hr.fim)] = set()
                    horarios[(dia, disc_hr.inicio, disc_hr.fim)].add(disc.id)

    return horarios

def salva_horarios(horarios: _ExtracaoHorarios, nome_horarios: Path|str, nome_horarios_turmas: Path|str) -> None:
    """Salva os horários e as turmas que os ocupam em arquivos CSV.
    Args:
        horarios: Dicionário retornado por `extrai_horarios_e_turmas`
        nome_horarios: Nome do arquivo CSV para salvar os horários
        nome_horarios_turmas: Nome do arquivo CSV para salvar as turmas que ocupam os horários
    """

    def _salva_horarios(horarios: _ExtracaoHorarios, nome: Path|str) -> None:
        """Salva os horários em um arquivo CSV"""
        with open(nome, 'w', encoding='utf-8') as f:
            f.write('ID;DIA;INICIO;FIM\n')
            for _id, (dia, inicio, fim) in enumerate(horarios, start=1):
                f.write(f"{_id};{dia.name.capitalize()};{inicio};{fim}\n")

    def _salva_horarios_turmas(horarios: _ExtracaoHorarios, nome: Path|str) -> None:
        """Salva os horários e as turmas que os ocupam em um arquivo CSV"""
        with open(nome, 'w', encoding='utf-8') as f:
            f.write('TURMA_ID;HORARIO_ID\n')
            for horario_id, turmas in enumerate(horarios.values(), start=1):
                for turma_id in turmas:
                    f.write(f"{turma_id};{horario_id}\n")

    _salva_horarios(horarios, nome_horarios)
    _salva_horarios_turmas(horarios, nome_horarios_turmas)