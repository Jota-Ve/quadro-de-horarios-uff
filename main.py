import logging

import horario
import quadro_de_horarios
from lista_disciplinas import DiaDaSemana
import cli

logging.basicConfig(level=logging.INFO)


def main():
    args = cli.pega_argumentos()
    logging.debug(f"Argumentos: {args}")
    
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(*args.ano_semestre)
    # quadro.seleciona_vagas_para_curso(args.curso)
    lista_disc = quadro.pesquisa(args.pesquisa)
    
    disciplinas = lista_disc.selecionar_horarios(args.horarios)

    print(f"Filtrando horários: {'\n'.join(map(str, lista_disc.disciplinas))}")
    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()