import contextlib
import io
import unittest

from intermediate.tac import GeneradorTAC
from main import compilar, main as ejecutar_main, validar
from vm.maquina_virtual import MaquinaVirtual


class GeneracionYEjecucion(unittest.TestCase):
    def ejecutar_codigo(self, codigo, max_pasos=10000):
        _, arbol, _ = validar(codigo)
        tac = GeneradorTAC().generar(arbol)
        maquina = MaquinaVirtual(tac)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            resultados = maquina.ejecutar(max_pasos=max_pasos)
        return tac, resultados, salida.getvalue(), maquina

    def test_aritmetica_asignacion_e_impresion(self):
        tac, resultados, texto, maquina = self.ejecutar_codigo(
            "entero x = 2 + 3 * 4; imprimir x;"
        )
        self.assertEqual(resultados, [14])
        self.assertIn("('+', '2', '@t1'", repr(tac))
        self.assertIn(">> SALIDA: 14", texto)
        self.assertEqual(maquina.memoria["x"], 14)

    def test_modulo_personal_llega_hasta_la_vm(self):
        tac, resultados, texto, _ = self.ejecutar_codigo(
            "entero numero = 10; entero divisor = 3; "
            "entero residuo = numero % divisor; imprimir residuo;"
        )
        self.assertIn(("%", "numero", "divisor", "@t1"), tac)
        self.assertEqual(resultados, [1])
        self.assertIn(">> SALIDA: 1", texto)

    def test_precedencia_modulo_y_multiplicacion(self):
        _, resultados, _, _ = self.ejecutar_codigo(
            "imprimir 10 % 3 * 2;"
        )
        self.assertEqual(resultados, [2])

    def test_negacion_unaria(self):
        _, resultados, _, _ = self.ejecutar_codigo("imprimir -7 + 2;")
        self.assertEqual(resultados, [-5])

    def test_si_ejecuta_solo_si_la_condicion_es_verdadera(self):
        _, resultados, _, _ = self.ejecutar_codigo(
            "entero x = 2; si (x > 1) { imprimir x; } "
            "si (x < 1) { imprimir 99; }"
        )
        self.assertEqual(resultados, [2])

    def test_mientras_recalcula_condicion_en_cada_iteracion(self):
        _, resultados, _, _ = self.ejecutar_codigo(
            "entero x = 0; mientras (x < 3) { imprimir x; x = x + 1; }"
        )
        self.assertEqual(resultados, [0, 1, 2])

    def test_operadores_relacionales_retornan_cero_o_uno(self):
        operadores = ("==", "!=", "<", ">", "<=", ">=")
        fuente = " ".join(f"imprimir 2 {op} 3;" for op in operadores)
        _, resultados, _, _ = self.ejecutar_codigo(fuente)
        self.assertEqual(resultados, [0, 1, 1, 0, 1, 0])

    def test_declaracion_sin_inicializador_no_crea_valor(self):
        _, arbol = compilar("entero x;")
        tac = GeneradorTAC().generar(arbol)
        self.assertEqual(tac, [])

    def test_lectura_antes_de_asignar_falla_en_ejecucion(self):
        _, arbol, _ = validar("entero x; imprimir x;")
        tac = GeneradorTAC().generar(arbol)
        with self.assertRaisesRegex(NameError, "'x' sin valor"):
            MaquinaVirtual(tac).ejecutar()

    def test_modulo_por_cero_falla_en_ejecucion(self):
        _, arbol, _ = validar("entero residuo = 10 % 0; imprimir residuo;")
        tac = GeneradorTAC().generar(arbol)
        with self.assertRaisesRegex(ZeroDivisionError, "Módulo entre cero"):
            MaquinaVirtual(tac).ejecutar()

    def test_division_por_cero_falla_en_ejecucion(self):
        _, arbol, _ = validar("entero cociente = 10 / 0;")
        tac = GeneradorTAC().generar(arbol)
        with self.assertRaisesRegex(ZeroDivisionError, "División entre cero"):
            MaquinaVirtual(tac).ejecutar()

    def test_limite_de_pasos_detiene_ciclo_infinito(self):
        _, arbol, _ = validar("mientras (1 < 2) { }")
        tac = GeneradorTAC().generar(arbol)
        with self.assertRaisesRegex(RuntimeError, "Se superaron 10 pasos"):
            MaquinaVirtual(tac).ejecutar(max_pasos=10)

    def test_etiqueta_de_salto_desconocida(self):
        maquina = MaquinaVirtual([("JMP", None, None, "@L99")])
        with self.assertRaisesRegex(ValueError, "Etiqueta de salto desconocida"):
            maquina.ejecutar()

    def test_etiqueta_duplicada_es_rechazada(self):
        tac = [
            ("LABEL", None, None, "@L1"),
            ("LABEL", None, None, "@L1"),
        ]
        with self.assertRaisesRegex(ValueError, "Etiqueta repetida"):
            MaquinaVirtual(tac)

    def test_argumento_de_operacion_desconocido(self):
        maquina = MaquinaVirtual([])
        with self.assertRaisesRegex(NotImplementedError, r"Operador '\^'"):
            maquina.instruccion_operacion("^", "2", "3", "@t1")

    def test_cli_ejecuta_pipeline_y_puntos_de_corte(self):
        opciones = ([], ["--solo-lexer"], ["--solo-parser"],
                    ["--solo-semantica"], ["--solo-tac"])
        for opcion in opciones:
            with self.subTest(opcion=opcion):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida):
                    codigo = ejecutar_main(
                        ["pruebas/17_modulo_personal.txt", *opcion]
                    )
                texto = salida.getvalue()
                self.assertEqual(codigo, 0)
                self.assertIn("=== TOKENS ===", texto)
                if opcion == []:
                    self.assertIn("=== EJECUCIÓN EN MÁQUINA VIRTUAL ===", texto)
                    self.assertIn("Salidas VM: [1]", texto)
                if opcion == ["--solo-tac"]:
                    self.assertIn("=== CÓDIGO INTERMEDIO TAC ===", texto)
                    self.assertNotIn("=== EJECUCIÓN EN MÁQUINA VIRTUAL ===", texto)

    def test_cli_informa_error_de_ejecucion_y_devuelve_codigo_uno(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = ejecutar_main(["pruebas/18_error_modulo_cero.txt"])
        self.assertEqual(codigo, 1)
        self.assertIn("[Error VM] Módulo entre cero.", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
