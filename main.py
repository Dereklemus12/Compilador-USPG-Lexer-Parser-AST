"""Punto de entrada para ejecutar el compilador completo."""

from pathlib import Path
from pprint import pprint

from intermediate.tac import GeneradorTAC
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analizador import AnalizadorSemantico
from vm.maquina_virtual import MaquinaVirtual


def compilar(codigo):
    """Ejecuta Lexer y Parser. Se conserva el contrato de las entregas previas."""
    tokens = Lexer(codigo).analizar()
    return tokens, Parser(tokens).parsear()


def validar(codigo):
    """Ejecuta Lexer, Parser y semántica, y devuelve tokens, AST y analizador."""
    tokens, ast = compilar(codigo)
    semantico = AnalizadorSemantico()
    semantico.analizar(ast)
    return tokens, ast, semantico


def main(argv=None):
    import argparse

    argumentos = argparse.ArgumentParser(
        description="Compilador: Lexer, Parser, AST, Semántica, TAC y VM"
    )
    argumentos.add_argument(
        "archivo", nargs="?", default="pruebas/01_basico_valido.txt",
        help="archivo de código fuente (por defecto: pruebas/01_basico_valido.txt)",
    )
    fases = argumentos.add_mutually_exclusive_group()
    fases.add_argument("--solo-lexer", action="store_true", help="detenerse tras los tokens")
    fases.add_argument("--solo-parser", action="store_true", help="detenerse tras el AST")
    fases.add_argument("--solo-semantica", action="store_true", help="detenerse tras validar tipos")
    fases.add_argument("--solo-tac", action="store_true", help="mostrar TAC sin ejecutar la VM")
    argumentos.add_argument(
        "--limite-pasos", type=int, default=10000,
        help="máximo de instrucciones ejecutadas por la VM (por defecto: 10000)",
    )
    opciones = argumentos.parse_args(argv)

    archivo = Path(opciones.archivo)
    if not archivo.is_absolute() and not archivo.exists():
        archivo = Path(__file__).resolve().parent / archivo

    semantico = None
    try:
        codigo = archivo.read_text(encoding="utf-8")

        tokens = Lexer(codigo).analizar()
        print("=== TOKENS ===")
        pprint(tokens)
        if opciones.solo_lexer:
            return 0

        ast = Parser(tokens).parsear()
        print("=== AST ===")
        pprint(ast)
        if opciones.solo_parser:
            return 0

        print("=== SEMÁNTICA ===")
        semantico = AnalizadorSemantico()
        semantico.analizar(ast)
        print("Análisis semántico correcto.")
        print("=== TABLA DE SÍMBOLOS (GLOBAL: nombre -> tipo) ===")
        pprint(semantico.tabla_simbolos)
        if opciones.solo_semantica:
            return 0

        tac = GeneradorTAC().generar(ast)
        print("=== CÓDIGO INTERMEDIO TAC ===")
        pprint(tac)
        if opciones.solo_tac:
            return 0

        print("=== EJECUCIÓN EN MÁQUINA VIRTUAL ===")
        maquina = MaquinaVirtual(tac)
        salidas = maquina.ejecutar(max_pasos=opciones.limite_pasos)
        print("Salidas VM:", salidas)
        return 0
    except (
        OSError,
        UnicodeError,
        SyntaxError,
        NameError,
        TypeError,
        ValueError,
        ZeroDivisionError,
        RuntimeError,
    ) as error:
        print(error)
        if semantico is not None:
            print("Tabla parcial al detenerse en el primer error:")
            pprint(semantico.tabla_simbolos)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
