from pathlib import Path
from pprint import pprint
from lexer.lexer import Lexer
from parser.parser import Parser


def compilar(codigo):
    tokens = Lexer(codigo).analizar()
    return tokens, Parser(tokens).parsear()


if __name__ == '__main__':
    import sys
    archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('pruebas/01_basico_valido.txt')
    codigo = archivo.read_text(encoding='utf-8')
    tokens, ast = compilar(codigo)
    print('=== TOKENS ===')
    pprint(tokens)
    print('=== AST ===')
    pprint(ast)
