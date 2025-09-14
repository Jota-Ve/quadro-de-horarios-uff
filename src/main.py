import argparse
import asyncio
import datetime
import logging
from typing import Iterable, Literal

import aiohttp

import cli
import curso
import extracao
import quadro_de_horarios

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)



def gera_semestres(inicio: tuple[int, int], fim: tuple[int, int]|None=None) -> Iterable[tuple[int, Literal[1, 2]]]:
    """Gera semestres a partir de um ano e semestre inicial até um ano e semestre final"""
    def _antes_do_semestre_incial(ano: int, sem: int) -> bool: return (ano, sem) < (ano_inicial, sem_inicial)
    def _depois_do_semestre_final(ano: int, sem: int) -> bool: return (ano, sem) > (ano_final, sem_final)

    if fim is None:
        hoje = datetime.date.today()
        fim = (hoje.year, 1 if hoje.month <= 6 else 2)

    ano_inicial, sem_inicial, ano_final, sem_final = inicio + fim

    for ano in range(ano_inicial, ano_final + 1):
        for sem in (1, 2):
            if _antes_do_semestre_incial(ano, sem):
                continue
            if _depois_do_semestre_final(ano, sem):
                break

            yield (ano, sem)




async def main(args: argparse.Namespace):
    logger.debug(f"Argumentos: {args}")
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_localidade('Niterói')
    quadro.seleciona_vagas_para_curso(args.curso)

    LIMITE = asyncio.Semaphore(25)
    ESPERA = (0.03, 0.5)
    disciplinas : dict[str, str] = {}
    turmas      : dict[int, tuple] = {}
    horarios    : extracao._ExtracaoHorarios = {}
    cursos      : set[curso.Curso] = set()
    vagas       : dict[int, dict[curso.Curso, dict[str, int]]] = {}

    try:
        async with aiohttp.ClientSession() as session:
            for ano, semestre in gera_semestres((2015, 1), (2025, 2)):
                quadro.seleciona_semestre(ano, semestre)
                logger.info(f"Pesquisando {ano} / {semestre}...")

                listas_turmas = await quadro.async_pesquisa(session, LIMITE, "", espera=ESPERA)

                disciplinas.update(extracao.extrai_disciplinas(listas_turmas))
                turmas.update(extracao.extrai_turmas(listas_turmas))
                for horario, turmas_ in extracao.extrai_horarios_e_turmas(listas_turmas).items():
                    horarios.setdefault(horario, set()).update(turmas_)

                # Processa as disciplinas e extrai informações de vagas e horários de forma assíncrona
                for lista in listas_turmas:
                    tasks = [tur.async_info(session, LIMITE, espera_aleatoria=ESPERA) for tur in lista.turmas]
                    for coro in asyncio.as_completed(tasks):
                        info = await coro
                        # ignora turmas q nao possuem informações, como as de yoga de 2009/2
                        # ignora turmas sem vagas alocadas, como: https://app.uff.br/graduacao/quadrodehorarios/turmas/100000019624
                        if (info is None) or (not info.vagas):
                            continue

                        cursos.update(info.vagas.keys())
                        vagas[info.id] = info.vagas

        logging.info("Extração concluída.")
    finally:
        extracao.salva_discipllinas(disciplinas, 'extracao/disciplinas.csv')
        extracao.salva_turmas(turmas, 'extracao/turmas.csv')
        extracao.salva_cursos(cursos, 'extracao/cursos.csv')
        extracao.salva_horarios(horarios, 'extracao/horarios.csv', 'extracao/horarios_turmas.csv')
        extracao.salva_vagas(vagas, 'extracao/vagas.csv')



if __name__ == '__main__':
    args = cli.pega_argumentos()
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
                        handlers=[
                            logging.FileHandler('main.log', encoding='utf-8'),
                            logging.StreamHandler()
                        ],
                        level=logging.DEBUG if args.debug else logging.INFO)

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.warning("Execução interrompida pelo teclado")
    except Exception:
        logger.critical("Erro inesperado:", exc_info=True)
    finally:
        logger.info("Execução finalizada")