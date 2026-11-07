"""Regenera evidencias auténticas. Ejecutar desde la raíz del repositorio."""
from pathlib import Path
import os
import subprocess
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from main import compilar
from semantic.analizador import AnalizadorSemantico


def generar():
    destino = RAIZ / 'evidencias' / 'semantico'
    destino.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.discover(str(RAIZ / 'pruebas'), pattern='test_*.py')
    with (destino / 'pruebas_completas.txt').open('w', encoding='utf-8') as salida:
        salida.write(f'Python {sys.version}\nComando: python -m unittest discover -s pruebas -p "test_*.py" -v\n\n')
        resultado = unittest.TextTestRunner(stream=salida, verbosity=2).run(suite)
    if not resultado.wasSuccessful():
        raise RuntimeError('Las pruebas fallaron; revisar pruebas_completas.txt')
    casos = [(f'{i:02}_', 0 if i in (1, 2, 3, 7, 13) else 1)
             for i in range(1, 17)]
    for prefijo, esperado in casos:
        archivo = next((RAIZ / 'pruebas').glob(prefijo + '*.txt'))
        ejecucion = subprocess.run([sys.executable, str(RAIZ / 'main.py'), str(archivo)],
                                  cwd=RAIZ, capture_output=True, text=True, encoding='utf-8',
                                  env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        (destino / (archivo.stem + '.txt')).write_text(
            f'Comando: python main.py pruebas/{archivo.name}\nCódigo de salida: {ejecucion.returncode}\n\n'
            + ejecucion.stdout + ejecucion.stderr, encoding='utf-8')
        if ejecucion.returncode != esperado:
            raise AssertionError(f'{archivo.name}: salida {ejecucion.returncode}, esperada {esperado}')
    codigo = (RAIZ / 'pruebas/07_token_personalizado.txt').read_text(encoding='utf-8')
    sem = AnalizadorSemantico()
    _, ast = compilar(codigo)
    with (destino / 'evolucion_tabla_simbolos.txt').open('w', encoding='utf-8') as salida:
        salida.write('Programa: pruebas/07_token_personalizado.txt\nÁmbito global; no se calculan valores.\n')
        salida.write(f'Inicial: {sem.tabla_simbolos}\n')
        for indice, sentencia in enumerate(ast.sentencias, 1):
            sem.analizar(sentencia)
            salida.write(f'{indice}. {type(sentencia).__name__}: {sem.tabla_simbolos}\n')
    (destino / 'resumen.txt').write_text(
        f'Pruebas ejecutadas: {resultado.testsRun}\nFallos: {len(resultado.failures)}\n'
        f'Errores: {len(resultado.errors)}\nOmitidas: {len(resultado.skipped)}\n'
        f'Programas CLI verificados: {len(casos)} (5 válidos; 11 errores esperados).\n'
        'Tokens y AST presentes en los casos sintácticamente válidos.\n'
        'Módulo: 07_token_personalizado válido; 16_error_modulo_booleano rechazado.\n'
        'Tabla global: ver evolucion_tabla_simbolos.txt.\n', encoding='utf-8')
    print((destino / 'resumen.txt').read_text(encoding='utf-8'))


if __name__ == '__main__':
    generar()
