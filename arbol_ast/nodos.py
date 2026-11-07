from dataclasses import dataclass, field
from typing import Any

class NodoAST:
    """Base común para el visitante semántico del docente."""


@dataclass
class Programa(NodoAST):
    sentencias: list

@dataclass
class Declaracion(NodoAST):
    nombre: str
    valor: Any = None
    linea: int = field(default=1, repr=False, compare=False)

    tipo = property(lambda self: 'entero')
    id = property(lambda self: self.nombre)
    expr = property(lambda self: self.valor)

@dataclass
class Asignacion(NodoAST):
    nombre: str
    valor: Any
    linea: int = field(default=1, repr=False, compare=False)

    id = property(lambda self: self.nombre)
    expr = property(lambda self: self.valor)

@dataclass
class Numero(NodoAST):
    valor: int

@dataclass
class Identificador(NodoAST):
    nombre: str
    linea: int = field(default=1, repr=False, compare=False)

@dataclass
class OpBinaria(NodoAST):
    izquierda: Any
    operador: str
    derecha: Any

    izq = property(lambda self: self.izquierda)
    op = property(lambda self: self.operador)
    der = property(lambda self: self.derecha)

@dataclass
class Si(NodoAST):
    condicion: Any
    cuerpo: list

    bloque_v = property(lambda self: self.cuerpo)

@dataclass
class Mientras(NodoAST):
    condicion: Any
    cuerpo: list

    bloque = property(lambda self: self.cuerpo)

@dataclass
class Imprimir(NodoAST):
    expresion: Any

    expr = property(lambda self: self.expresion)
