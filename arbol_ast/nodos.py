from dataclasses import dataclass
from typing import Any

@dataclass
class Programa:
    sentencias: list

@dataclass
class Declaracion:
    nombre: str
    valor: Any = None

@dataclass
class Asignacion:
    nombre: str
    valor: Any

@dataclass
class Numero:
    valor: int

@dataclass
class Identificador:
    nombre: str

@dataclass
class OpBinaria:
    izquierda: Any
    operador: str
    derecha: Any

@dataclass
class Si:
    condicion: Any
    cuerpo: list

@dataclass
class Mientras:
    condicion: Any
    cuerpo: list

@dataclass
class Imprimir:
    expresion: Any
