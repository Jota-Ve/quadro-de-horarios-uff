import itertools
import logging
from pathlib import Path
import time
from typing import Sequence
import relatorio
from datetime import datetime

logger = logging.getLogger(__name__)


def salva_reprovados(departamento: str, arquivo: str|Path='extracao/reprovados.csv', anos: Sequence[int]|None=None):
    logger.debug(f"Argumentos: {departamento=}, {arquivo=}, {anos=}")
    if anos is None: anos = range(2011, datetime.today().year)

    rel = relatorio.Relatorios()
    assert (departamento_atual := rel.seleciona_departamento(departamento))
    logger.info(f"Salvando reprovados de {departamento_atual} entre {anos[0]} e {anos[-1]} em {arquivo!r}")

    with open(arquivo, 'w', encoding="utf-8") as f:
        # Cabeçalho
        f.write('ANO_SEMESTRE;CODIGO;DISCIPLINA;DEPARTAMENTO;REPROVADOS\n')

        for ano, semestre in itertools.product(anos, [1, 2]):
            time.sleep(1)
            dados_reprovacao = rel.abre_reprovados(ano, semestre)
            assert dados_reprovacao, "Não conseguiu extrair dados de reprovados"

            for codigo, disciplina, reprovados in dados_reprovacao:
                f.write(';'.join([f'{ano}{semestre}', codigo, disciplina, departamento_atual, f'{reprovados}']) + '\n')
