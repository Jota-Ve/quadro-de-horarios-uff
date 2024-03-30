import argparse


def pega_argumentos():
    parser = argparse.ArgumentParser()
    parser.add_argument('pesquisa', help='Código ou Nome da disciplina', default='')
    parser.add_argument('-curso', help='Curso para qual a disciplina precisa ter vagas', default='')
    # parser.add_argument('-seg', help='Horários disponíveis na segunda', default='', nargs='*')
    parser.add_argument('-ano_semestre', help='Ano e semstre das disciplinas', type=int, default=(None, None), nargs=2)

    return parser.parse_args()
