import enum
import re
from collections import abc
from typing import Any


class DiaDaSemana(enum.StrEnum):
    SEGUNDA = "horario-segunda"
    TERCA   = "horario-terca"
    QUARTA  = "horario-quarta"
    QUINTA  = "horario-quinta"
    SEXTA   = "horario-sexta"
    SABADO  = "horario-sabado"



class Horario(abc.Container[str]):
    __slots__ = ('__horario', '__inicio', '__fim')

    RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')

    # Formato HH:MM-HH:MM, 24h
    RGXP_HHMM_HHMM = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d))-(([01]\d|2[0-3]):([0-5]\d))$')

    @property
    def inicio(self): return self.__inicio
    @property
    def fim(self): return self.__fim


    def __init__(self, horario: str) -> None:
        if not self.valido(horario):
            raise ValueError(f"{horario!r} não está no padrão esperado: {self.RGXP_HHMM_HHMM.pattern!r}")

        self.__horario = horario
        self.__inicio = horario[:5]
        self.__fim = horario[6:]


    def __str__(self) -> str:
        return self.__horario


    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({self.__horario!r})'


    def __contains__(self, x: Any) -> bool:
        if isinstance(x, self.__class__):
            return self.__inicio <= x.__inicio <= x.__fim <= self.__fim
        if isinstance(x, str) and self.valido(x):
            inicio, fim = x.split('-')
            return self.__inicio <= inicio <= fim <= self.__fim

        return False


    @classmethod
    def valido(cls, horario: str) -> bool:
        return ((match := cls.RGXP_HHMM_HHMM.fullmatch(horario)) is not None
                and match.group(1) < match.group(4))