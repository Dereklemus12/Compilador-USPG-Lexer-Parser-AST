from typing import NamedTuple

class Token(NamedTuple):
    tipo: str
    valor: str
    linea: int
    columna: int = 1
