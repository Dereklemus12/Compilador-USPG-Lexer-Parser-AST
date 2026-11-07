"""Fase 3, integrada desde la plantilla de ciarenasg-uspg.

Visitor con tabla GLOBAL {nombre: tipo}. Las expresiones devuelven
'entero' o 'booleano'; las sentencias devuelven None. Sin ejecución ni TAC.
Procedencia y diferencias: docs/06_GUIA_ANALISIS_SEMANTICO.md.
"""
from typing import Dict, Optional
from arbol_ast.nodos import (
    NodoAST, Programa, Declaracion, Asignacion, Numero, Identificador,
    OpBinaria, Imprimir, Si, Mientras,
)


class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos: Dict[str, str] = {}

    def analizar(self, nodo: NodoAST) -> Optional[str]:
        metodo = f'visitar_{type(nodo).__name__}'
        visitante = getattr(self, metodo, self.error_generico)
        return visitante(nodo)

    def error_generico(self, nodo: NodoAST):
        raise NotImplementedError(
            f'Falta soporte semantico para el nodo {type(nodo).__name__}. '
            'Si agregaste nodos AST por tus tokens propios, implementa su visitante.'
        )

    def visitar_Programa(self, nodo: Programa) -> None:
        for sentencia in nodo.sentencias:
            self.analizar(sentencia)

    def visitar_Numero(self, nodo: Numero) -> str:
        return 'entero'

    def visitar_Imprimir(self, nodo: Imprimir) -> None:
        self.analizar(nodo.expr)

    def visitar_Declaracion(self, nodo: Declaracion) -> None:
        if nodo.id in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Línea {nodo.linea}: variable '{nodo.id}' ya declarada."
            )
        # La sintaxis propia admite 'entero x;'. No se exige inicialización.
        # Registrar DESPUÉS del inicializador impide la autorreferencia.
        if nodo.expr is not None:
            tipo_expr = self.analizar(nodo.expr)
            if tipo_expr != nodo.tipo:
                raise TypeError(
                    f"[Error Semantico] Línea {nodo.linea}: inicialización de '{nodo.id}' "
                    f"exige '{nodo.tipo}', se recibió '{tipo_expr}'."
                )
        self.tabla_simbolos[nodo.id] = nodo.tipo

    def visitar_Asignacion(self, nodo: Asignacion) -> None:
        if nodo.id not in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Línea {nodo.linea}: variable '{nodo.id}' no declarada."
            )
        tipo_expr = self.analizar(nodo.expr)
        tipo_variable = self.tabla_simbolos[nodo.id]
        if tipo_expr != tipo_variable:
            raise TypeError(
                f"[Error Semantico] Línea {nodo.linea}: asignación a '{nodo.id}' "
                f"exige '{tipo_variable}', se recibió '{tipo_expr}'."
            )

    def visitar_Identificador(self, nodo: Identificador) -> str:
        if nodo.nombre not in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Línea {nodo.linea}: variable '{nodo.nombre}' no declarada."
            )
        return self.tabla_simbolos[nodo.nombre]

    def visitar_OpBinaria(self, nodo: OpBinaria) -> str:
        tipo_izq = self.analizar(nodo.izq)
        tipo_der = self.analizar(nodo.der)
        aritmeticos = {'+', '-', '*', '/', '%'}
        relacionales = {'==', '!=', '<', '>', '<=', '>='}
        if nodo.op in aritmeticos or nodo.op in relacionales:
            if tipo_izq != 'entero' or tipo_der != 'entero':
                raise TypeError(
                    f"[Error Semantico] Operador '{nodo.op}' exige "
                    f"dos enteros, se recibieron '{tipo_izq}' y '{tipo_der}'."
                )
            return 'entero' if nodo.op in aritmeticos else 'booleano'
        raise TypeError(
            f"[Error Semantico] Operador '{nodo.op}' sin regla semantica. "
            'Si es una extension personal, define su validacion y tipo de resultado.'
        )

    def visitar_Si(self, nodo: Si) -> None:
        tipo = self.analizar(nodo.condicion)
        if tipo != 'booleano':
            raise TypeError(
                f"[Error Semantico] Condición de 'si' exige 'booleano', se recibió '{tipo}'."
            )
        for sentencia in nodo.bloque_v:
            self.analizar(sentencia)

    def visitar_Mientras(self, nodo: Mientras) -> None:
        tipo = self.analizar(nodo.condicion)
        if tipo != 'booleano':
            raise TypeError(
                f"[Error Semantico] Condición de 'mientras' exige 'booleano', se recibió '{tipo}'."
            )
        for sentencia in nodo.bloque:
            self.analizar(sentencia)
