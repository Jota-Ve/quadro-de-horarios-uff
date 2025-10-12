import argparse
import asyncio
import datetime
import logging
from typing import Iterable, Literal

import aiohttp

import cli
import curso
import extracao
import lista_disciplinas
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


def atualiza_disciplinas_turmas_e_horarios(
    lista_turmas: lista_disciplinas.ListaTurmas,
    disciplinas: dict[str, str],
    turmas: dict[int, tuple],
    horarios: extracao._ExtracaoHorarios
    ) -> None:
    """Atualiza os dados extraídos com as informações de uma lista de turmas.

    Parameters
    ----------
    lista_turmas : lista_disciplinas.ListaTurmas
        A lista de turmas a ser processada.
    disciplinas : dict[str, str]
        Dicionário onde as chaves são os códigos das disciplinas e os valores são os nomes.
    turmas : dict[int, tuple]
        Dicionário onde as chaves são os IDs das turmas e os valores são tuplas com informações básicas.
    horarios : extracao._ExtracaoHorarios
        Dicionário onde as chaves são tuplas (dia_da_semana, hora_inicio, hora_fim) e os valores são conjuntos de IDs das turmas que ocupam aquele horário.
    """
    # Atualiza disciplinas
    disciplinas.update(extracao.extrai_disciplinas(lista_turmas))
    # Atualiza turmas
    turmas.update(extracao.extrai_turmas(lista_turmas))
    # Atualiza horários
    for horario, turmas_ in extracao.extrai_horarios_e_turmas(lista_turmas).items():
        horarios.setdefault(horario, set()).update(turmas_)


async def main(args: argparse.Namespace):
    logger.debug(f"Argumentos: {args}")
    quadro = quadro_de_horarios.QuadroDeHorarios()

    quadro.seleciona_localidade('Niterói')
    if args.curso:
        quadro.seleciona_vagas_para_curso(args.curso)

    LIMITE = asyncio.Semaphore(50)  # Limite de requisições assíncronas simultâneas
    ESPERA = (.01, 1.5)
    disciplinas : dict[str, str] = {}
    turmas      : dict[int, tuple] = {}
    horarios    : extracao._ExtracaoHorarios = {}
    cursos      : set[curso.Curso] = set()
    vagas       : set[lista_disciplinas.T_Vagas] = set()

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession(headers=headers) as session:
            for ano, semestre in gera_semestres((2025, 1), (2025, 2)):
                quadro.seleciona_semestre(ano, semestre)
                logger.info(f"Pesquisando {ano} / {semestre}...")
                tasks = []

                try:
                    async for lista_turmas in quadro.async_pesquisa(session, LIMITE, "", espera_aleatoria=ESPERA):
                        atualiza_disciplinas_turmas_e_horarios(lista_turmas, disciplinas=disciplinas, turmas=turmas, horarios=horarios)

                        # Cria e inicia as requisições assíncronas de todas as turmas da página/lista de turmas
                        tasks += [asyncio.create_task(tur.async_info(session, LIMITE, espera_aleatoria=ESPERA)) for tur in lista_turmas.turmas]

                    # Processa as requisições e extrai informações de vagas e horários de forma assíncrona
                    for coro in asyncio.as_completed(tasks):
                        info = await coro
                        # ignora turmas q nao possuem informações, como as de yoga de 2009/2
                        # ignora turmas sem vagas alocadas, como: https://app.uff.br/graduacao/quadrodehorarios/turmas/100000019624
                        if (info is None) or (not info.vagas):
                            continue

                        cursos.update(vaga.curso for vaga in info.vagas)
                        vagas.update(info.vagas)

                finally:
                    for unfinished_task in [t for t in tasks if not t.done()]:
                        unfinished_task.cancel()

        logging.info("Extração concluída com sucesso.")
    finally:
        logging.info("Salvando resultados...")
        extracao.salva_disciplinas(disciplinas, 'extracao/disciplinas.csv')
        extracao.salva_turmas(turmas, 'extracao/turmas.csv')
        extracao.salva_cursos(cursos, 'extracao/cursos.csv')
        extracao.salva_horarios(horarios, 'extracao/horarios.csv', 'extracao/horarios_turmas.csv')
        extracao.salva_vagas(vagas, 'extracao/vagas.csv')



if __name__ == '__main__':
    t0 = datetime.datetime.now()
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
        logger.info(f"Execução finalizada em {(datetime.datetime.now() - t0).total_seconds():.0f} segundos (começou em {t0})")