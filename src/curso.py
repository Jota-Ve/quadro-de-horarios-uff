import re
import dataclasses
from typing import Self


@dataclasses.dataclass(frozen=True, slots=True)
class Curso:
    id: int
    nome: str

    @classmethod
    def from_string(cls, val: str) -> Self:
        """Cria uma instância de Curso a partir de uma string no formato 'ID - Nome'.
        >>> Curso.from_string('059 - Relações Internacionais')
        Curso(id=59, nome='Relações Internacionais')
        """

        if (match := re.match(r'(\d+) - (.+)', val)) is None:
            raise ValueError(f"Curso inválido: {val!r}")

        _id = int(match.group(1))
        nome = match.group(2).strip()
        return cls(_id, nome)


    def __hash__(self) -> int:
        return self.id


    def __str__(self) -> str:
        return f'{self.id:03d} - {self.nome}'
