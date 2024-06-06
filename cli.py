import argparse
import dataclasses
from collections import abc
import re
import horario
import lista_disciplinas



def filtra_horario(args) -> dict[lista_disciplinas.DiaDaSemana, list[horario.Horario]]:
    horarios = {}

    if args.seg: horarios[lista_disciplinas.DiaDaSemana.SEGUNDA] = args.seg
    if args.ter: horarios[lista_disciplinas.DiaDaSemana.TERCA] = args.ter
    if args.qua: horarios[lista_disciplinas.DiaDaSemana.QUARTA] = args.qua
    if args.qui: horarios[lista_disciplinas.DiaDaSemana.QUINTA] = args.qui
    if args.sex: horarios[lista_disciplinas.DiaDaSemana.SEXTA] = args.sex
    if args.sab: horarios[lista_disciplinas.DiaDaSemana.SABADO] = args.sab

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

    args = parser.parse_args()
    args.horarios = filtra_horario(args)
    return args
