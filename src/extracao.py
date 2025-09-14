
import itertools
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Literal, Sequence

import curso
import horario
import relatorio
from lista_disciplinas import ListaTurmas

logger = logging.getLogger(__name__)


def salva_reprovados(rel: relatorio.Relatorios, departamentos: Iterable[str]='', arquivo: str|Path='extracao/reprovados.csv', anos: Sequence[int]|None=None):
    if anos is None: anos = range(2015, datetime.today().year)
    if not departamentos: departamentos = rel.lista_departamentos()

    # with open(arquivo, 'w', encoding="utf-8") as f:
        # Cabeçalho
        # f.write('CODIGO;ANO;SEMESTRE;DEPARTAMENTO;REPROVADOS\n')

    for departamento in departamentos:
        assert (departamento_atual := rel.seleciona_departamento(departamento))
        logger.info(f"Salvando reprovados de {departamento_atual} entre {anos[0]} e {anos[-1]}")

        for ano, semestre in itertools.product(anos, (1, 2)):
            if (ano) == (datetime.today().year):
                break  # Não extrai dados do semestre atual pq ainda não existem

            time.sleep((random.random() * 3) + 1)
            dados_reprovacao = rel.baixa_xls_reprovados(ano, semestre)
            # assert dados_reprovacao, "Não conseguiu extrair dados de reprovados"
            # for codigo, _, reprovados in dados_reprovacao:
            #     f.write(';'.join([codigo, f'{ano}', f'{semestre}', departamento_atual, f'{reprovados}']) + '\n')

            logger.info(f"Baixou reprovados de {ano}/{semestre} - {departamento_atual}")


def extrai_disciplinas(listas_turmas: Iterable[ListaTurmas]) -> dict[str, str]:
    """Extrai código e nome das disciplinas.

    Parameters
    ----------
    listas_turmas : Iterable[ListaTurmas]
        Listas de turmas das quais extrair as disciplinas.

    Returns
    -------
    dict[str, str]
        Dicionário onde as chaves são os códigos das disciplinas e os valores são os nomes.
    """
    return {tur.codigo_disciplina: tur.nome_disciplina for lista in listas_turmas for tur in lista.turmas}

def salva_disciplinas(disciplinas: dict[str, str], nome: Path|str) -> None:
    """Salva as disciplinas em um arquivo CSV.

    Parameters
    ----------
    disciplinas : dict[str, str]
        Dicionário onde as chaves são os códigos das disciplinas e os valores são os nomes.
    nome : Path | str
        Nome do arquivo CSV onde as disciplinas serão salvas.
    """
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('CODIGO;NOME\n')
        for codigo, nome in sorted(disciplinas.items()):
            f.write(f"{codigo};{nome}\n")


type TurmaRow = tuple[str, str, int|None, int, int, str, None]
def extrai_turmas(lista_disc: Iterable[ListaTurmas]):
    """Extrai informações básicas das turmas de uma lista de ListaTurmas.

    Parameters
    ----------
    lista_disc : Iterable[ListaTurmas]
        Listas de turmas das quais extrair as informações.

    Returns
    -------
    dict[int, TurmaRow]
        Dicionário onde as chaves são os IDs das turmas e os valores são tuplas com as seguintes informações:
        (nome, tipo_de_oferta, modulo, ano, semestre, codigo_disciplina, professor).
    """
    turmas: dict[int, TurmaRow] = {}
    for lista in lista_disc:
        for disc in lista.turmas:
            ano, semestre = map(int, [disc.ano_semestre[:4], disc.ano_semestre[4]])
            turmas[disc._id] = (disc.nome, disc.tipo_de_oferta, disc.modulo, ano, semestre, disc.codigo_disciplina, None)

    return turmas

def salva_turmas(turmas: dict[int, TurmaRow], nome: Path|str) -> None:
    """Salva as turmas em um arquivo CSV.
        Parameters
        ----------
        turmas : dict[int, TurmaRow]
            Dicionário onde as chaves são os IDs das turmas e os valores são tuplas com as seguintes informações:
            (nome, tipo_de_oferta, modulo, ano, semestre, codigo_disciplina, professor).
        nome : Path | str
            Nome do arquivo CSV onde as turmas serão salvas.
    """
    def _sanitiza_valores_invalidos(x) -> Literal['NULL']|str:
        return 'NULL' if x in {None, '-'} else str(x)

    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;TURMA;TIPO_DE_OFERTA;CARGA_HORARIA;ANO;SEMESTRE;DISCIPLINA;PROFESSOR\n')
        for id_, outras_colunas in sorted(turmas.items()):
            f.write(f"{id_};" + ';'.join(map(_sanitiza_valores_invalidos, outras_colunas)) + "\n")


def salva_cursos(cursos: Iterable[curso.Curso], nome: Path|str) -> None:
    """Salva os cursos em um arquivo CSV.
    Parameters
    ----------
    cursos : Iterable[curso.Curso]
        Cursos a serem salvos.
    nome : Path | str
        Nome do arquivo CSV onde os cursos serão salvos.
    """
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('ID;NOME\n')
        for _curso in sorted(cursos, key=lambda x: x.id):
            f.write(f"{_curso.id};{_curso.nome}\n")


type VagasRow = dict[curso.Curso, dict[str, int]]
def salva_vagas(vagas: dict[int, VagasRow], nome: Path|str) -> None:
    """ Salva as vagas em um arquivo CSV.
    Parameters
    ----------
    vagas : dict[int, dict[curso.Curso, dict[str, int]]]
        Dicionário onde as chaves são os IDs das turmas e os valores são dicionários
        onde as chaves são os cursos e os valores são dicionários com as seguintes informações:
        'vagas_regular', 'vagas_vestibular', 'inscritos_regular', 'inscritos_vestibular', 'excedentes', 'candidatos'.
    nome : Path | str
        Nome do arquivo CSV onde as vagas serão salvas.
    """
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('TURMA_ID;CURSO_ID;VAGAS_REGULAR;VAGAS_VESTIBULAR;INSCRITOS_REGULAR;INSCRITOS_VESTIBULAR;EXCEDENTES;CANDIDATOS\n')
        for turma_id, cursos in sorted(vagas.items()):
            for _curso, info in cursos.items():
                f.write(f"{turma_id};{_curso.id};{info.get('vagas_regular', 0)};{info.get('vagas_vestibular', 0)};"
                        f"{info.get('inscritos_regular', 0)};{info.get('inscritos_vestibular', 0)};"
                        f"{info.get('excedentes', 0)};{info.get('candidatos', 0)}\n")


_ExtracaoHorarios = dict[tuple[horario.DiaDaSemana, str, str], set[int]]
def extrai_horarios_e_turmas(iter_listas_turmas: Iterable[ListaTurmas]) -> _ExtracaoHorarios:
    """Extrai horários de uma lista de ListaTurmas e os IDs das turmas que os ocupam.

    Retorna um dicionário onde as chaves são tuplas (dia_da_semana, hora_inicio, hora_fim)
    e os valores são conjuntos de IDs das turmas que ocupam aquele horário.
    """
    horarios: _ExtracaoHorarios = dict()
    for lista in iter_listas_turmas:
        for disc in lista.turmas:
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