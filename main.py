from pathlib import Path
from pprint import pprint
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analizador import AnalizadorSemantico


def compilar(codigo):
    tokens = Lexer(codigo).analizar()
    return tokens, Parser(tokens).parsear()


def validar(codigo):
    """Flujo completo. compilar conserva su retorno histórico (tokens, AST)."""
    tokens, ast = compilar(codigo)
    semantico = AnalizadorSemantico()
    semantico.analizar(ast)
    return tokens, ast, semantico


def main(argv=None):
    import argparse
    argumentos = argparse.ArgumentParser(description='Lexer + Parser + AST + Semántica')
    argumentos.add_argument('archivo', nargs='?', default='pruebas/01_basico_valido.txt')
    fases = argumentos.add_mutually_exclusive_group()
    fases.add_argument('--solo-lexer', action='store_true')
    fases.add_argument('--solo-parser', action='store_true')
    opciones = argumentos.parse_args(argv)
    archivo = Path(opciones.archivo)
    if not archivo.is_absolute() and not archivo.exists():
        archivo = Path(__file__).resolve().parent / archivo
    semantico = None
    try:
        codigo = archivo.read_text(encoding='utf-8')
        tokens = Lexer(codigo).analizar()
        print('=== TOKENS ===')
        pprint(tokens)
        if opciones.solo_lexer:
            return 0
        ast = Parser(tokens).parsear()
        print('=== AST ===')
        pprint(ast)
        if opciones.solo_parser:
            return 0
        print('=== SEMANTICA ===')
        semantico = AnalizadorSemantico()
        semantico.analizar(ast)
        print('Análisis semántico correcto. No se ejecutan instrucciones.')
        print('=== TABLA DE SIMBOLOS (GLOBAL: nombre -> tipo) ===')
        pprint(semantico.tabla_simbolos)
        return 0
    except (OSError, UnicodeError, SyntaxError, NameError, TypeError) as error:
        print(error)
        if semantico is not None:
            print('Tabla parcial al detenerse en el primer error:')
            pprint(semantico.tabla_simbolos)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
