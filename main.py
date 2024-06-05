from datetime import datetime
import logging
from typing import Iterable

import quadro_de_horarios
from lista_disciplinas import DiaDaSemana, ListaDisciplinas

logging.basicConfig(level=logging.INFO)


def salva_disciplinas_e_horarios(lista_disc: Iterable[ListaDisciplinas]):
    for lista in lista_disc:
        for disciplina in lista.disciplinas:
            with (open(f'disciplinas-{datetime.now().isoformat()}.csv', 'w', encoding='utf-8') as f_disc,
                  open(f'horarios-{datetime.now().isoformat()}.csv', 'w', encoding='utf-8') as f_hora):

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
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(2024, 1)
    quadro.seleciona_vagas_para_curso("Sistemas de informação")
    lista_disc = quadro.pesquisa()
    # print(f"\nDisciplinas: {lista_disc.nome_disciplinas()}\n")

    salva_disciplinas_e_horarios(lista_disc)

    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()