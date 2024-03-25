import logging

import quadro_de_horarios
from lista_disciplinas import DiaDaSemana

logging.basicConfig(level=logging.DEBUG)


def main():
    quadro = quadro_de_horarios.QuadroDeHorarios()
    quadro.seleciona_ano_semestre(2024, 1)
    quadro.seleciona_vagas_para_curso("Sistemas de informação")
    lista_disc = quadro.pesquisa()
    print(f"\nDisciplinas: {lista_disc.nome_disciplinas()}\n")
    
    print(lista_disc.horarios({
        DiaDaSemana.SEGUNDA: ["00:00-23:59"],
        DiaDaSemana.TERCA: ["12:00-23:59"]}
    ))
    print("")
    # lista_disc.salvar_HTML("test_busca.html")


if __name__ == '__main__':
    main()