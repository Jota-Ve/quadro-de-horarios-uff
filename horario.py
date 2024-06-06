from collections import abc
import re
from typing import Self


class Horario(abc.Container):
    __slots__ = ('__horario', '__inicio', '__fim')
    
    RGXP_HORARIO = re.compile(r'^\d\d:\d\d-\d\d:\d\d')

    @property
    def inicio(self): return self.__inicio
    @property
    def fim(self): return self.__fim
    
    
    def __init__(self, horario: str) -> None:
        # super().__init__()
        if not self.RGXP_HORARIO.fullmatch(horario):
            raise ValueError(f"{horario!r} não está no padrão esperado: {self.RGXP_HORARIO.pattern!r}")
        
        self.__horario = horario
        self.__inicio = horario[:5]
        self.__fim = horario[6:]
    
    
    def __str__(self) -> str:
        return self.__horario
    
    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({self.__horario})'
    
    
    def __contains__(self, x) -> bool:
        if isinstance(x, self.__class__):
            return self.__inicio <= x.__inicio <= x.__fim <= self.__fim
        if isinstance(x, str) and self.RGXP_HORARIO.fullmatch(x):
            inicio, fim = x.split('-')
            return self.__inicio <= inicio <= fim <= self.__fim
         
        return False
    