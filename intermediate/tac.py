"""Generador de código intermedio TAC a partir del AST validado.

Cada instrucción tiene la forma (operación, argumento1, argumento2, destino).
Los temporales (@tN) y etiquetas (@LN) son nombres internos.
"""

from typing import List, Optional, Tuple

from arbol_ast.nodos import (
    NodoAST,
    Programa,
    Declaracion,
    Asignacion,
    Numero,
    Identificador,
    OpBinaria,
    Imprimir,
    Si,
    Mientras,
)


Instruccion = Tuple[str, Optional[str], Optional[str], Optional[str]]


class GeneradorTAC:
    """Convierte sentencias y expresiones AST a instrucciones de tres direcciones."""

    def __init__(self):
        self.instrucciones: List[Instruccion] = []
        self.conteo_temp = 0
        self.conteo_etiquetas = 0

    def nuevo_temp(self) -> str:
        self.conteo_temp += 1
        return f"@t{self.conteo_temp}"

    def nueva_etiqueta(self) -> str:
        self.conteo_etiquetas += 1
        return f"@L{self.conteo_etiquetas}"

    def emitir(
        self,
        op: str,
        arg1: Optional[str] = None,
        arg2: Optional[str] = None,
        res: Optional[str] = None,
    ) -> None:
        self.instrucciones.append((op, arg1, arg2, res))

    def generar(self, nodo: NodoAST) -> List[Instruccion]:
        """Visita un nodo y devuelve las instrucciones acumuladas."""
        metodo = f"generar_{type(nodo).__name__}"
        visitante = getattr(self, metodo, self.error_generico)
        visitante(nodo)
        return self.instrucciones

    def error_generico(self, nodo: NodoAST):
        raise NotImplementedError(
            f"No existe generación TAC para {type(nodo).__name__}. "
            "Adapta la extensión personal correspondiente."
        )

    def generar_Programa(self, nodo: Programa) -> None:
        for sentencia in nodo.sentencias:
            self.generar(sentencia)

    def generar_Declaracion(self, nodo: Declaracion) -> None:
        # Una declaración sin inicializador no define un valor en memoria.
        # La VM reportará el uso antes de asignación cuando se lea esa variable.
        if nodo.expr is None:
            return
        fuente = self.evaluar_expr(nodo.expr)
        self.emitir("ASSIGN", fuente, None, nodo.id)

    def generar_Asignacion(self, nodo: Asignacion) -> None:
        fuente = self.evaluar_expr(nodo.expr)
        self.emitir("ASSIGN", fuente, None, nodo.id)

    def generar_Imprimir(self, nodo: Imprimir) -> None:
        fuente = self.evaluar_expr(nodo.expr)
        self.emitir("PRINT", fuente)

    def generar_Si(self, nodo: Si) -> None:
        etiqueta_fin = self.nueva_etiqueta()
        condicion = self.evaluar_expr(nodo.condicion)
        self.emitir("JMP_FALSE", condicion, None, etiqueta_fin)
        for sentencia in nodo.bloque_v:
            self.generar(sentencia)
        self.emitir("LABEL", None, None, etiqueta_fin)

    def generar_Mientras(self, nodo: Mientras) -> None:
        etiqueta_inicio = self.nueva_etiqueta()
        etiqueta_fin = self.nueva_etiqueta()
        self.emitir("LABEL", None, None, etiqueta_inicio)
        # La condición se emite después de la etiqueta de inicio para que cada
        # vuelta del ciclo vuelva a calcular su valor.
        condicion = self.evaluar_expr(nodo.condicion)
        self.emitir("JMP_FALSE", condicion, None, etiqueta_fin)
        for sentencia in nodo.bloque:
            self.generar(sentencia)
        self.emitir("JMP", None, None, etiqueta_inicio)
        self.emitir("LABEL", None, None, etiqueta_fin)

    def evaluar_expr(self, nodo: NodoAST) -> str:
        if isinstance(nodo, Numero):
            return str(nodo.valor)
        if isinstance(nodo, Identificador):
            return nodo.nombre
        if isinstance(nodo, OpBinaria):
            izquierda = self.evaluar_expr(nodo.izq)
            derecha = self.evaluar_expr(nodo.der)
            temporal = self.nuevo_temp()
            # OpBinaria conserva el operador original, incluido el módulo (%).
            self.emitir(nodo.op, izquierda, derecha, temporal)
            return temporal
        raise NotImplementedError(
            f"No existe generación TAC para la expresión {type(nodo).__name__}. "
            "Adapta la extensión personal correspondiente."
        )
