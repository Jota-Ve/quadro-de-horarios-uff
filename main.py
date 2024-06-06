from datetime import datetime
import logging
from pathlib import Path
from typing import Iterable, Literal

import horario
import quadro_de_horarios
from lista_disciplinas import ListaDisciplinas
import cli

logging.basicConfig(level=logging.INFO)


def salva_disciplinas_e_horarios(it_list_disc: Iterable[ListaDisciplinas], nome_disciplinas: Path|str, nome_horarios: Path|str, modo: Literal['w', 'a']):
    cabecalho_disciplinas = modo == 'w' or not Path(nome_disciplinas).exists()
    cabecalho_horarios    = modo == 'w' or not Path(nome_horarios).exists()
    
    with (open(nome_disciplinas, modo, encoding='utf-8') as f_disc,
            open(nome_horarios, modo, encoding='utf-8') as f_hora):

        if cabecalho_disciplinas:
            f_disc.write('ANO_SEMESTRE;TIPO_DE_OFERTA;CODIGO;NOME;MODULO;TURMA\n')
        if cabecalho_horarios:
            f_hora.write('ANO_SEMESTRE;CODIGO;TURMA;DIA;INICIO;FIM\n')

        for lista in it_list_disc:
            for disciplina in lista.disciplinas:
                # Disciplinas
                f_disc.write(';'.join([
                    disciplina.ano_semestre, disciplina.tipo_de_oferta,
                    disciplina.codigo, disciplina.nome, disciplina.modulo,
                    disciplina.turma
                ]) + '\n')

                # Horários
                for dia, horarios in disciplina.horario.items():
                    for hora in horarios:
                        f_hora.write(';'.join([
                            disciplina.ano_semestre, disciplina.codigo,
                            disciplina.turma, dia.name, hora.inicio, hora.fim
                        ]) + '\n')


def main():
    args = cli.pega_argumentos()
    logging.debug(f"Argumentos: {args}")
    
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_vagas_para_curso("Sistemas de informação")
    for ano in range(2009, 2025):
        for semestre in range(1, 3):
            quadro.seleciona_semestre(ano, semestre)
            logging.info(f"Pesquisando {ano} / {semestre}...")
            lista_disc = quadro.pesquisa(espera=1)
            salva_disciplinas_e_horarios(lista_disc, 'disciplinas.csv', 'horarios.csv', 'w')


if __name__ == '__main__':
    main()