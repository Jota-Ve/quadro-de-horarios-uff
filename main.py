import argparse
import asyncio
import datetime
import logging
from pathlib import Path
from typing import Iterable, Literal

import aiohttp

import cli
import quadro_de_horarios
from lista_disciplinas import ListaDisciplinas


logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


async def salva_disciplinas_e_horarios(session: aiohttp.ClientSession, limite: asyncio.Semaphore, it_list_disc: Iterable[ListaDisciplinas], nome_disciplinas: Path|str, nome_horarios: Path|str, nome_vagas: str|Path, espera: tuple[float, float]=(0,.7)):
    cabecalho_disciplinas = not Path(nome_disciplinas).exists()
    cabecalho_horarios    = not Path(nome_horarios).exists()
    cabecalho_vagas       = not Path(nome_vagas).exists()

    with (open(nome_disciplinas, 'a', encoding='utf-8') as f_disc,
            open(nome_horarios, 'a', encoding='utf-8') as f_hora,
            open(nome_vagas, 'a', encoding='utf-8') as f_vagas):

        if cabecalho_disciplinas:
            f_disc.write('ANO_SEMESTRE;CODIGO;TURMA;TIPO_DE_OFERTA;NOME;MODULO;LINK\n')
        if cabecalho_horarios:
            f_hora.write('ANO_SEMESTRE;CODIGO;TURMA;DIA;INICIO;FIM\n')
        if cabecalho_vagas:
            f_vagas.write('ANO_SEMESTRE;CODIGO;TURMA;NOME;VAGAS_REGULAR;VAGAS_VESTIBULAR;INSCRITOS_REGULAR;INSCRITOS_VESTIBULAR;EXCEDENTES;CANDIDATOS\n')


        for lista in it_list_disc:
            tasks = [disc.async_info(session, limite, espera_aleatoria=espera) for disc in lista.disciplinas]
            info_list = await asyncio.gather(*tasks)

            for disciplina, info in zip(lista.disciplinas, info_list):
                # ignora turmas q nao possuem informações, como as de yoga de 2009/2
                if info is None: continue
                # ignora turmas sem vagas alocadas, como: https://app.uff.br/graduacao/quadrodehorarios/turmas/100000019624
                if not info.vagas:
                    continue

                for curso, vagas in info.vagas.items():
                    linha_vagas = ';'.join([
                        info.ano_semestre,
                        info.codigo,
                        info.turma,
                        curso,
                        str(vagas['vagas_regular']),
                        str(vagas['vagas_vestibular']),
                        str(vagas['inscritos_regular']),
                        str(vagas['inscritos_vestibular']),
                        str(vagas['excedentes']),
                        str(vagas['candidatos']),
                    ]) + '\n'

                    f_vagas.write(linha_vagas)

                # Disciplinas
                f_disc.write(';'.join([
                    disciplina.ano_semestre, disciplina.codigo, disciplina.turma,
                    disciplina.tipo_de_oferta, disciplina.nome, disciplina.modulo,
                    disciplina.link_info
                ]) + '\n')

                # Horários
                for dia, horarios in disciplina.horario.items():
                    for hora in horarios:
                        f_hora.write(';'.join([
                            disciplina.ano_semestre, disciplina.codigo,
                            disciplina.turma, dia.name, hora.inicio, hora.fim
                        ]) + '\n')


async def extracao(quadro: quadro_de_horarios.QuadroDeHorarios, ano_semestre: Iterable[tuple[int, Literal[1,2]]], pesquisa: str=''):
    nome_disciplinas = Path('disciplinas.csv')
    nome_horarios = Path('horarios.csv')
    nome_vagas = Path('vagas.csv')

    nome_disciplinas.unlink(missing_ok=True)
    nome_horarios.unlink(missing_ok=True)
    nome_vagas.unlink(missing_ok=True)

    LIMITE = asyncio.Semaphore(15)
    ESPERA = (0.05, 0.75)
    async with aiohttp.ClientSession() as session:
        for ano, semestre in ano_semestre:
            quadro.seleciona_semestre(ano, semestre)
            logger.info(f"Pesquisando {ano} / {semestre}...")
            lista_disc = await quadro.async_pesquisa(session, LIMITE, pesquisa, espera=ESPERA)
            await salva_disciplinas_e_horarios(session, LIMITE, lista_disc, nome_disciplinas, nome_horarios, nome_vagas, espera=ESPERA)


async def salva_turmas(args: argparse.Namespace):
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_localidade('Niterói')
    # if args.curso:
    #     quadro.seleciona_vagas_para_curso(args.curso)
    # quadro.seleciona_vagas_para_curso('sistemas de informação')

    hoje = datetime.date.today()
    await extracao(quadro,
             [(ano, sem) for ano in range(2015, 2025) for sem in (1,2)
              if not (ano==hoje.year and sem==hoje.month//6)])


async def main(args: argparse.Namespace):
    logger.debug(f"Argumentos: {args}")
    await salva_turmas(args)


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