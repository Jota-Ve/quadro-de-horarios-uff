import logging
from pathlib import Path
from typing import Iterable, Literal

import cli
import quadro_de_horarios
import relatorio
from lista_disciplinas import ListaDisciplinas


def salva_disciplinas_e_horarios(it_list_disc: Iterable[ListaDisciplinas], nome_disciplinas: Path|str, nome_horarios: Path|str, nome_vagas: str|Path):
    modo = 'a'
    cabecalho_disciplinas = modo == 'w' or not Path(nome_disciplinas).exists()
    cabecalho_horarios    = modo == 'w' or not Path(nome_horarios).exists()
    cabecalho_vagas    = modo == 'w' or not Path(nome_vagas).exists()

    with (open(nome_disciplinas, modo, encoding='utf-8') as f_disc,
            open(nome_horarios, modo, encoding='utf-8') as f_hora,
            open(nome_vagas, modo, encoding='utf-8') as f_vagas):

        if cabecalho_disciplinas:
            f_disc.write('ANO_SEMESTRE;CODIGO;TURMA;TIPO_DE_OFERTA;NOME;MODULO;LINK\n')
        if cabecalho_horarios:
            f_hora.write('ANO_SEMESTRE;CODIGO;TURMA;DIA;INICIO;FIM\n')
        if cabecalho_vagas:
            f_vagas.write('ANO_SEMESTRE;CODIGO;TURMA;NOME;VAGAS_REGULAR;VAGAS_VESTIBULAR;INSCRITOS_REGULAR;INSCRITOS_VESTIBULAR;EXCEDENTES;CANDIDATOS\n')

        for lista in it_list_disc:
            for disciplina in lista.disciplinas:
                # Vagas
                info = disciplina.info()
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


def extracao(quadro: quadro_de_horarios.QuadroDeHorarios, ano_semestre: Iterable[tuple[int, Literal[1,2]]], pesquisa: str):
    for ano, semestre in ano_semestre:
        quadro.seleciona_semestre(ano, semestre)
        logging.info(f"Pesquisando {ano} / {semestre}...")
        lista_disc = quadro.pesquisa(pesquisa, espera=0)
        salva_disciplinas_e_horarios(lista_disc, 'disciplinas.csv', 'horarios.csv', 'vagas.csv')


def main(args):
    logger.debug(f"Argumentos: {args}")

    # quadro = quadro_de_horarios.QuadroDeHorarios()
    # quadro.seleciona_vagas_para_curso("Sistemas de informação")

    rel = relatorio.Relatorios()
    assert rel.seleciona_departamento("sistemas de informação")

    with open("reprovados.csv", "a", encoding="utf-8") as f:
        # Cabeçalho
        f.write('ANO_SEMESTRE;CODIGO;DISCIPLINA;DEPARTAMENTO;REPROVADOS\n')

        departamento = rel.departamento_atual()
        for ano in range(2011, 2024):
            for semestre in (1,2):
                dados_reprovacao = rel.abre_reprovados(ano, semestre)
                assert dados_reprovacao, "Não conseguiu extrair dados de reprovados"

                for codigo, disciplina, reprovados in dados_reprovacao:
                    f.write(';'.join([f'{ano}{semestre}', codigo, disciplina, departamento, f'{reprovados}']) + '\n')


if __name__ == '__main__':
    args = cli.pega_argumentos()
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', 
                        handlers=[
                            logging.FileHandler('main.log', encoding='utf-8'),
                            logging.StreamHandler()
                        ],
                        level=logging.DEBUG if args.debug else logging.INFO)
    
    main(args)