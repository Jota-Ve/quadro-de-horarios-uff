import logging

import quadro_de_horarios
from lista_disciplinas import DiaDaSemana

logging.basicConfig(level=logging.INFO)


def main():
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(2024, 1)
    quadro.seleciona_vagas_para_curso("Sistemas de informação")
    lista_disc = quadro.pesquisa()
    # print(f"\nDisciplinas: {lista_disc.nome_disciplinas()}\n")
    
    disciplinas = lista_disc.selecionar_horarios({
        DiaDaSemana.SEGUNDA: ["00:00-22:00"],
        DiaDaSemana.TERCA: ["18:00-23:59"],
        DiaDaSemana.QUARTA: ["20:00-23:59"],
        
        }
    )

    print('\n'.join(map(str, disciplinas)))
    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()