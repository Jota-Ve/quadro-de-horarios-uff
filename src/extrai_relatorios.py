import itertools
import logging
from pathlib import Path
import time
from typing import Iterable, Sequence
import relatorio
from datetime import datetime

logger = logging.getLogger(__name__)


def salva_reprovados(rel: relatorio.Relatorios, departamentos: Iterable[str]='', arquivo: str|Path='extracao/reprovados.csv', anos: Sequence[int]|None=None):
    if anos is None: anos = range(2015, datetime.today().year)
    if not departamentos: departamentos = rel.lista_departamentos()

    with open(arquivo, 'w', encoding="utf-8") as f:
        # Cabeçalho
        f.write('CODIGO;ANO;SEMESTRE;DEPARTAMENTO;REPROVADOS\n')

        for departamento in departamentos:
            assert (departamento_atual := rel.seleciona_departamento(departamento))
            logger.info(f"Salvando reprovados de {departamento_atual} entre {anos[0]} e {anos[-1]} em {arquivo!r}")

            for ano, semestre in itertools.product(anos, (1, 2)):
                if (ano, semestre) == (datetime.today().year, datetime.today().month // 6):
                    break  # Não extrai dados do semestre atual pq ainda não existem

                time.sleep(2)
                dados_reprovacao = rel.abre_reprovados(ano, semestre)
                assert dados_reprovacao, "Não conseguiu extrair dados de reprovados"
                for codigo, _, reprovados in dados_reprovacao:
                    f.write(';'.join([codigo, f'{ano}', f'{semestre}', departamento_atual, f'{reprovados}']) + '\n')

                logger.info(f"Salvou {len(dados_reprovacao)} reprovados de {ano}/{semestre}")
