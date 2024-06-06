from datetime import datetime
import logging
from typing import Iterable

import horario
import quadro_de_horarios
from lista_disciplinas import DiaDaSemana, ListaDisciplinas
import cli

logging.basicConfig(level=logging.INFO)


def salva_disciplinas_e_horarios(lista_disc: Iterable[ListaDisciplinas], nome_disciplinas, nome_horarios, modo):
    with (open(nome_disciplinas, modo, encoding='utf-8') as f_disc,
            open(nome_horarios, modo, encoding='utf-8') as f_hora):

        # Cabeçalhos
        if modo == 'w':
            f_disc.write('ANO_SEMESTRE;TIPO_DE_OFERTA;CODIGO;NOME;MODULO;TURMA\n')
            f_hora.write('ANO_SEMESTRE;CODIGO;TURMA;DIA;INICIO;FIM\n')

        for lista in lista_disc:
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
                            disciplina.turma, dia.name, hora[:5], hora[6:]
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
            lista_disc = quadro.pesquisa(espera=0)
            salva_disciplinas_e_horarios(lista_disc, 'disciplinas.csv', 'horarios.csv', 'a')


if __name__ == '__main__':
    main()