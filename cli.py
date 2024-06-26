import argparse
from collections import abc
import horario



def filtra_horario(args) -> dict[horario.DiaDaSemana, list[horario.Horario]]:
    horarios = {}

    if args.seg: horarios[horario.DiaDaSemana.SEGUNDA] = args.seg
    if args.ter: horarios[horario.DiaDaSemana.TERCA] = args.ter
    if args.qua: horarios[horario.DiaDaSemana.QUARTA] = args.qua
    if args.qui: horarios[horario.DiaDaSemana.QUINTA] = args.qui
    if args.sex: horarios[horario.DiaDaSemana.SEXTA] = args.sex
    if args.sab: horarios[horario.DiaDaSemana.SABADO] = args.sab

    return horarios


def pega_argumentos():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pesquisa', help='Código ou Nome da disciplina', default='')
    parser.add_argument('-curso', help='Curso para qual a disciplina precisa ter vagas', default='')
    parser.add_argument('-seg', help='Horários disponíveis na segunda', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-ter', help='Horários disponíveis na terça', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-qua', help='Horários disponíveis na quarta', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-qui', help='Horários disponíveis na quinta', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-sex', help='Horários disponíveis na sexta', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-sab', help='Horários disponíveis no sábado', type=horario.Horario, default=[], nargs='*')
    parser.add_argument('-ano_semestre', help='Ano e semstre das disciplinas', type=int, default=(None, None), nargs=2)
    parser.add_argument('-debug', help='Executando em modo DEBUG', action='store_true')

    args = parser.parse_args()
    args.horarios = filtra_horario(args)
    return args
