"""Máquina virtual educativa que interpreta instrucciones TAC."""

from typing import Dict, List, Optional

from intermediate.tac import Instruccion


OPERADORES = {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">="}


class MaquinaVirtual:
    def __init__(self, tac: List[Instruccion]):
        self.tac = list(tac)
        self.memoria: Dict[str, int] = {}
        self.ip = 0
        self.salidas: List[int] = []
        self.etiquetas: Dict[str, int] = {}

        for indice, (op, _arg1, _arg2, resultado) in enumerate(self.tac):
            if op == "LABEL":
                if not resultado or resultado in self.etiquetas:
                    raise ValueError(
                        f"[Error VM] Etiqueta repetida o vacía: {resultado!r}"
                    )
                self.etiquetas[resultado] = indice

    def obtener_val(self, argumento: Optional[str]) -> int:
        """Lee un literal entero o un identificador/temporal ya asignado."""
        if argumento is None:
            raise ValueError("[Error VM] Falta operando obligatorio.")
        if argumento.lstrip("-").isdigit():
            return int(argumento)
        if argumento not in self.memoria:
            raise NameError(
                f"[Error VM] Variable/temporal '{argumento}' sin valor."
            )
        return self.memoria[argumento]

    def instruccion_asignar(
        self, fuente: Optional[str], destino: Optional[str]
    ) -> None:
        if not destino:
            raise ValueError("[Error VM] ASSIGN sin destino.")
        self.memoria[destino] = self.obtener_val(fuente)

    def ejecutar(self, max_pasos: int = 10000) -> List[int]:
        if max_pasos < 1:
            raise ValueError("max_pasos debe ser al menos 1.")

        pasos = 0
        while 0 <= self.ip < len(self.tac):
            if pasos >= max_pasos:
                raise RuntimeError(
                    f"[Límite de ejecución] Se superaron {max_pasos} pasos. "
                    "Revisa la condición del ciclo o incrementa el límite."
                )

            op, arg1, arg2, resultado = self.tac[self.ip]
            pasos += 1

            if op == "ASSIGN":
                self.instruccion_asignar(arg1, resultado)
            elif op in OPERADORES:
                self.instruccion_operacion(op, arg1, arg2, resultado)
            elif op == "PRINT":
                self.instruccion_imprimir(arg1)
            elif op == "JMP":
                self.instruccion_salto(resultado)
            elif op == "JMP_FALSE":
                self.instruccion_salto_condicional(arg1, resultado)
            elif op == "LABEL":
                # La etiqueta solo registra una posición de destino.
                pass
            else:
                raise NotImplementedError(
                    f"[Error VM] Instrucción '{op}' no soportada. "
                    "Agrega su ejecución a la máquina virtual."
                )

            # Los saltos posicionan ip en LABEL; el avance entra a la
            # instrucción que sigue a esa marca.
            self.ip += 1

        return self.salidas

    def _ubicacion_etiqueta(self, etiqueta: Optional[str]) -> int:
        if etiqueta not in self.etiquetas:
            raise ValueError(f"[Error VM] Etiqueta de salto desconocida: {etiqueta!r}")
        return self.etiquetas[etiqueta]

    def instruccion_operacion(
        self,
        op: str,
        arg1: Optional[str],
        arg2: Optional[str],
        resultado: Optional[str],
    ) -> None:
        if not resultado:
            raise ValueError("[Error VM] Operación sin destino.")

        izquierda = self.obtener_val(arg1)
        derecha = self.obtener_val(arg2)

        if op == "+":
            valor = izquierda + derecha
        elif op == "-":
            valor = izquierda - derecha
        elif op == "*":
            valor = izquierda * derecha
        elif op == "/":
            if derecha == 0:
                raise ZeroDivisionError("[Error VM] División entre cero.")
            valor = izquierda // derecha
        elif op == "%":
            if derecha == 0:
                raise ZeroDivisionError("[Error VM] Módulo entre cero.")
            valor = izquierda % derecha
        elif op == "==":
            valor = int(izquierda == derecha)
        elif op == "!=":
            valor = int(izquierda != derecha)
        elif op == "<":
            valor = int(izquierda < derecha)
        elif op == ">":
            valor = int(izquierda > derecha)
        elif op == "<=":
            valor = int(izquierda <= derecha)
        elif op == ">=":
            valor = int(izquierda >= derecha)
        else:
            raise NotImplementedError(f"[Error VM] Operador {op!r} sin ejecución.")

        self.memoria[resultado] = valor

    def instruccion_imprimir(self, fuente: Optional[str]) -> None:
        valor = self.obtener_val(fuente)
        self.salidas.append(valor)
        print(f">> SALIDA: {valor}")

    def instruccion_salto(self, etiqueta: Optional[str]) -> None:
        self.ip = self._ubicacion_etiqueta(etiqueta)

    def instruccion_salto_condicional(
        self, condicion: Optional[str], etiqueta: Optional[str]
    ) -> None:
        if self.obtener_val(condicion) == 0:
            self.ip = self._ubicacion_etiqueta(etiqueta)
