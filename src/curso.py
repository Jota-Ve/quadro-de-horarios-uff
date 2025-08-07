import re
import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class Curso:
    _id: int
    nome: str

    @classmethod
    def from_string(cls, val: str) -> None:
        """Cria uma instância de Curso a partir de uma string no formato 'ID - Nome'.
        >>> Curso.from_string('059 - Relações Internacionais')
        Curso(id_=59, nome='Relações Internacionais')
        """

        if (match := re.match(r'(\d+) - (.+)', val)) is None:
            raise ValueError(f"Curso inválido: {val!r}")

        _id = int(match.group(1))
        nome = match.group(2).strip()
        return cls(_id, nome) #type: ignore[return-value]


    def __hash__(self) -> int:
        return self._id


    def __str__(self) -> str:
        return f'{self._id:03d} - {self.nome}'


    @property
    def id(self) -> int:
        """Retorna o ID do curso"""
        return self._id