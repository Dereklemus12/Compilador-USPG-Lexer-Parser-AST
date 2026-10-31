import unittest
from main import compilar
from lexer.lexer import Lexer
from parser.parser import Parser
from arbol_ast.nodos import Declaracion, OpBinaria


class Integracion(unittest.TestCase):
    def test_eof(self):
        self.assertEqual(Lexer('entero x;').analizar()[-1].tipo, 'EOF')

    def test_valido(self):
        _, ast = compilar('entero x = 2; imprimir x;')
        self.assertEqual(len(ast.sentencias), 2)

    def test_precedencia(self):
        _, ast = compilar('entero x = 2 + 3 * 4;')
        e = ast.sentencias[0].valor
        self.assertIsInstance(e, OpBinaria)
        self.assertEqual(e.operador, '+')
        self.assertEqual(e.derecha.operador, '*')

    def test_error_sintactico(self):
        with self.assertRaises(SyntaxError):
            compilar('entero x = 10')

    def test_error_lexico(self):
        with self.assertRaises(SyntaxError):
            Lexer('entero x = @;').analizar()

    def test_token_anterior(self):
        self.assertEqual(Lexer('si (x >= 1) {}').analizar()[0].tipo, 'PR_SI')

    def test_operador_modulo(self):
        codigo = "entero residuo = 10 % 3;"

        tokens = Lexer(codigo).analizar()

        self.assertTrue(
            any(t.tipo == "OP_MODULO" and t.valor == "%" for t in tokens)
        )

        arbol = Parser(tokens).parsear()
        declaracion = arbol.sentencias[0]

        self.assertEqual(declaracion.valor.operador, "%")
        self.assertEqual(declaracion.valor.izquierda.valor, 10)
        self.assertEqual(declaracion.valor.derecha.valor, 3)


if __name__ == '__main__':
    unittest.main()
