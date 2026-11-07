"""Reglas del docente y extensiones, siempre desde la gramática real."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from arbol_ast.nodos import Identificador, Numero, OpBinaria, NodoAST
from main import compilar, main, validar
from semantic.analizador import AnalizadorSemantico


class Semantica(unittest.TestCase):
    def analizar(self, codigo):
        return validar(codigo)[2]

    def test_tabla_vacia(self):
        self.assertEqual(AnalizadorSemantico().tabla_simbolos, {})

    def test_numero(self):
        self.assertEqual(AnalizadorSemantico().analizar(Numero(12)), 'entero')

    def test_declaracion_valida(self):
        self.assertEqual(self.analizar('entero edad = 20;').tabla_simbolos, {'edad': 'entero'})

    def test_declaracion_sin_inicializador(self):
        self.assertEqual(self.analizar('entero x; x = 3; imprimir x;').tabla_simbolos, {'x': 'entero'})

    def test_no_exige_inicializacion(self):
        # La plantilla solo controla declaración y tipos, no asignación definida.
        self.assertEqual(self.analizar('entero x; imprimir x;').tabla_simbolos, {'x': 'entero'})

    def test_duplicada_con_linea(self):
        with self.assertRaisesRegex(NameError, "Línea 2:.*'x'.*ya declarada"):
            self.analizar('entero x = 1;\nentero x = 2;')

    def test_autorreferencia(self):
        with self.assertRaisesRegex(NameError, "'x'.*no declarada"):
            self.analizar('entero x = x + 1;')

    def test_no_registra_inicializador_invalido(self):
        sem = AnalizadorSemantico()
        with self.assertRaises(TypeError):
            sem.analizar(compilar('entero x = 1 < 2;')[1])
        self.assertEqual(sem.tabla_simbolos, {})

    def test_asignacion_valida(self):
        self.assertEqual(self.analizar('entero x = 5; x = x + 1;').tabla_simbolos, {'x': 'entero'})

    def test_asignacion_inexistente(self):
        with self.assertRaisesRegex(NameError, "Línea 2:.*'x'.*no declarada"):
            self.analizar('\nx = 10;')

    def test_identificador_inexistente(self):
        with self.assertRaisesRegex(NameError, "Línea 3:.*'y'.*no declarada"):
            self.analizar('\n\nentero x = y + 5;')

    def test_identificador_devuelve_tipo(self):
        sem = self.analizar('entero x = 2;')
        self.assertEqual(sem.analizar(Identificador('x')), 'entero')

    def test_inicializacion_incompatible(self):
        with self.assertRaisesRegex(TypeError, "inicialización.*'entero'.*'booleano'"):
            self.analizar('entero x = 5 < 10;')

    def test_asignacion_incompatible(self):
        with self.assertRaisesRegex(TypeError, "asignación.*'entero'.*'booleano'"):
            self.analizar('entero x = 5; x = x < 10;')

    def test_aritmeticos(self):
        for op in ('+', '-', '*', '/', '%'):
            with self.subTest(op=op):
                expresion = compilar(f'entero x = 10 {op} 3;')[1].sentencias[0].valor
                self.assertEqual(AnalizadorSemantico().analizar(expresion), 'entero')

    def test_aritmeticos_rechazan_booleanos_en_ambos_lados(self):
        for op in ('+', '-', '*', '/', '%'):
            for expr in (f'(1 < 2) {op} 3', f'3 {op} (1 < 2)'):
                with self.subTest(expr=expr), self.assertRaisesRegex(TypeError, 'dos enteros'):
                    self.analizar(f'entero x = {expr};')

    def test_relacionales(self):
        for op in ('==', '!=', '<', '>', '<=', '>='):
            with self.subTest(op=op):
                expresion = compilar(f'imprimir 1 {op} 2;')[1].sentencias[0].expresion
                self.assertEqual(AnalizadorSemantico().analizar(expresion), 'booleano')

    def test_relacion_rechaza_booleano(self):
        with self.assertRaisesRegex(TypeError, 'dos enteros'):
            self.analizar('imprimir (1 < 2) == (3 < 4);')

    def test_comparacion_encadenada_sigue_siendo_error_sintactico(self):
        with self.assertRaises(SyntaxError):
            compilar('si (1 < 3 < 5) { imprimir 3; }')

    def test_si_valido(self):
        self.assertEqual(self.analizar('entero x = 5; si (x < 10) { imprimir(x); }').tabla_simbolos, {'x': 'entero'})

    def test_si_entero_invalido(self):
        with self.assertRaisesRegex(TypeError, "Condición de 'si'.*'booleano'.*'entero'"):
            self.analizar('si (1) {}')

    def test_mientras_valido(self):
        self.assertEqual(self.analizar('entero x = 0; mientras (x < 3) { x = x + 1; }').tabla_simbolos, {'x': 'entero'})

    def test_mientras_entero_invalido(self):
        with self.assertRaisesRegex(TypeError, "Condición de 'mientras'"):
            self.analizar('mientras (3) {}')

    def test_visita_bloques_sin_ejecutar(self):
        for control in ('si', 'mientras'):
            with self.subTest(control=control), self.assertRaisesRegex(NameError, "'fantasma'"):
                self.analizar(f'{control} (1 > 2) {{ imprimir fantasma; }}')

    def test_alcance_global(self):
        sem = self.analizar('si (1 > 2) { entero local = 4; } imprimir local;')
        self.assertEqual(sem.tabla_simbolos, {'local': 'entero'})
        with self.assertRaisesRegex(NameError, 'ya declarada'):
            self.analizar('entero x; si (1 < 2) { entero x; }')

    def test_imprimir_identificador_inexistente(self):
        with self.assertRaisesRegex(NameError, "'fantasma'"):
            self.analizar('imprimir(fantasma);')

    def test_imprimir_booleano_valido(self):
        self.assertEqual(self.analizar('imprimir 1 < 2;').tabla_simbolos, {})

    def test_modulo_personal(self):
        ruta = Path(__file__).parent / '07_token_personalizado.txt'
        self.assertEqual(self.analizar(ruta.read_text(encoding='utf-8')).tabla_simbolos,
                         {'numero': 'entero', 'divisor': 'entero', 'residuo': 'entero'})

    def test_no_evalua_division_ni_modulo(self):
        # Son válidos por TIPOS; no se evalúa el divisor.
        self.assertEqual(self.analizar('entero x = 10 / 0; entero y = 10 % 0;').tabla_simbolos,
                         {'x': 'entero', 'y': 'entero'})

    def test_no_ejecuta_ciclo(self):
        self.assertEqual(self.analizar('mientras (1 < 2) { entero x = 3; }').tabla_simbolos, {'x': 'entero'})

    def test_negacion_y_precedencia(self):
        tokens, ast, sem = validar('entero x = -10 + 8 % 3 * 2;')
        self.assertTrue(any(t.tipo == 'OP_MODULO' for t in tokens))
        self.assertEqual(ast.sentencias[0].valor.derecha.operador, '*')
        self.assertEqual(ast.sentencias[0].valor.derecha.izquierda.operador, '%')
        self.assertEqual(sem.tabla_simbolos, {'x': 'entero'})

    def test_nodo_desconocido(self):
        with self.assertRaisesRegex(NotImplementedError, 'NodoAST'):
            AnalizadorSemantico().analizar(NodoAST())

    def test_operador_desconocido(self):
        # Defensa del visitante ante AST externo, no una extensión de gramática.
        with self.assertRaisesRegex(TypeError, 'sin regla semantica'):
            AnalizadorSemantico().analizar(OpBinaria(Numero(1), '^', Numero(2)))

    def test_cli_fases_y_error(self):
        with tempfile.TemporaryDirectory() as temporal:
            archivo = Path(temporal) / 'fuente.txt'
            archivo.write_text('imprimir inexistente;', encoding='utf-8')
            for opciones, esperado in (([], 1), (['--solo-parser'], 0), (['--solo-lexer'], 0)):
                with self.subTest(opciones=opciones):
                    salida = io.StringIO()
                    with contextlib.redirect_stdout(salida):
                        self.assertEqual(main([str(archivo), *opciones]), esperado)
                    if esperado == 1:
                        self.assertIn('no declarada', salida.getvalue())


if __name__ == '__main__':
    unittest.main()
