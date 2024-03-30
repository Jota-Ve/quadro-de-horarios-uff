import logging

import quadro_de_horarios
from lista_disciplinas import DiaDaSemana
import cli

logging.basicConfig(level=logging.INFO)


def main():
    args = cli.pega_argumentos()
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(*args.ano_semestre)
    quadro.seleciona_vagas_para_curso(args.curso)
    lista_disc = quadro.pesquisa(args.pesquisa)
    print(f"\nDisciplinas: {lista_disc.nome_disciplinas()}\n")
    
    disciplinas = lista_disc.selecionar_horarios({
        DiaDaSemana.SEGUNDA: ["00:00-22:00"],
        DiaDaSemana.TERCA: ["10:00-23:59"],
        DiaDaSemana.QUARTA: ["10:00-23:59"],
        
        }
    )

    print(f"Filtrando horários: {'\n'.join(map(str, disciplinas))}")
    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()