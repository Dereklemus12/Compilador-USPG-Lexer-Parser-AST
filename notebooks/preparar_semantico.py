"""Genera, ejecuta y valida el notebook académico desde los módulos reales."""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

RAIZ = Path(__file__).resolve().parents[1]


def preparar():
    nb = nbf.v4.new_notebook()
    nb.metadata.kernelspec = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
    nb.metadata.language_info = {'name': 'python', 'version': __import__('platform').python_version()}
    nb.cells = []

    def texto(contenido):
        nb.cells.append(nbf.v4.new_markdown_cell(contenido))

    def codigo(contenido):
        nb.cells.append(nbf.v4.new_code_cell(contenido))

    texto('''# Entrega 3 · Análisis semántico — USPG

## 1. Introducción al análisis semántico

Objetivo: continuar el compilador existente comprobando nombres y tipos del AST.
No se ejecutan instrucciones ni se genera TAC. Este notebook importa los módulos
reales, demuestra `%` y ejecuta la suite completa con assertions.

Fuente: [plantilla del docente](https://github.com/ciarenasg-uspg/compilador-entrega-semantica/blob/5fc51c0a3de764118b43cf6fac5645f730dde6b5/semantic/analizador.py).
El README enumera seis métodos; el archivo contiene cinco TODO porque el visitante
binario ya está implementado. Se completaron cinco y se amplió el binario para `%`.''')
    codigo('''from pathlib import Path
import sys
raiz = Path.cwd().resolve()
if not (raiz / 'main.py').is_file():
    raiz = raiz.parent
assert (raiz / 'semantic/analizador.py').is_file(), 'Ejecutar desde la raíz o notebooks/'
sys.path.insert(0, str(raiz))
from main import compilar, validar
from lexer.lexer import Lexer
from semantic.analizador import AnalizadorSemantico
print('Python:', sys.version.split()[0])
print('Importaciones del proyecto completas.')''')
    texto('''## 2. Errores léxicos, sintácticos y semánticos

El lexer rechaza caracteres desconocidos; el parser rechaza estructuras inválidas;
la semántica detecta incoherencias en programas con sintaxis válida. Capturamos
errores esperados y comprobamos su clase, sin ocultar excepciones inesperadas.''')
    codigo('''casos = [('léxico', 'entero x = @;', SyntaxError),
         ('sintáctico', 'entero x = ;', SyntaxError),
         ('semántico', 'imprimir desconocida;', NameError)]
for fase, fuente, esperado in casos:
    try:
        validar(fuente)
    except esperado as error:
        print(f'{fase}: {type(error).__name__}: {error}')
    else:
        raise AssertionError(f'No se detectó el error {fase}')''')
    texto('''## 3. Arquitectura Lexer → Parser → AST → Semántica

`compilar` conserva el retorno histórico `(tokens, ast)` y `validar` agrega el
analizador semántico. Visitor decide el método según la clase de cada nodo.''')
    codigo('''tokens, ast, sem = validar('entero edad = 20; imprimir edad;')
print('Tipos de token:', [t.tipo for t in tokens])
print('AST:', ast)
print('Tabla:', sem.tabla_simbolos)
assert tokens[-1].tipo == 'EOF'
assert sem.tabla_simbolos == {'edad': 'entero'}''')
    texto('''## 4. Concepto y funcionamiento de la tabla de símbolos

Diccionario global `{nombre: tipo}`. La presencia indica declaración. No guarda
valores, estado de inicialización ni ámbitos locales. Registramos después de
validar cada inicializador. Esta traza usa el ejemplo real del operador módulo.''')
    codigo('''fuente_modulo = (raiz / 'pruebas/07_token_personalizado.txt').read_text(encoding='utf-8')
_, arbol_modulo = compilar(fuente_modulo)
tabla = AnalizadorSemantico()
print('Inicial:', dict(tabla.tabla_simbolos))
for indice, sentencia in enumerate(arbol_modulo.sentencias, 1):
    tabla.analizar(sentencia)
    print(indice, type(sentencia).__name__, dict(tabla.tabla_simbolos))
assert tabla.tabla_simbolos == {'numero': 'entero', 'divisor': 'entero', 'residuo': 'entero'}''')
    texto('''## 5. Declaraciones e identificadores

Una declaración rechaza duplicados y comprueba el inicializador antes de registrar.
Un identificador debe existir y devuelve el tipo registrado. Se conserva `entero x;`:
la plantilla no exige comprobar inicialización.''')
    codigo('''def verificar_error(fuente, clase):
    try:
        validar(fuente)
    except clase as error:
        print(type(error).__name__, str(error))
    else:
        raise AssertionError('Se esperaba ' + clase.__name__)

verificar_error('entero x = x + 1;', NameError)
verificar_error('entero x = 1; entero x = 2;', NameError)
assert validar('entero x; imprimir x;')[2].tabla_simbolos == {'x': 'entero'}''')
    texto('''## 6. Validación de tipos y operaciones

Los literales y variables tienen tipo entero. `+ - * / %` requieren enteros y
devuelven entero. `== != < > <= >=` requieren enteros y devuelven booleano.
No se declaran variables booleanas, pero las comparaciones permiten comprobar
errores de tipo representables. `imprimir` admite cualquier expresión válida.''')
    codigo('''for expresion in ('5 + 3 * 2', '10 / 3', '1 < 2', '3 >= 1'):
    expr = compilar('imprimir ' + expresion + ';')[1].sentencias[0].expresion
    print(expresion, '→', AnalizadorSemantico().analizar(expr))
verificar_error('entero x = 1 < 2;', TypeError)
verificar_error('entero x = 2; x = 1 < 2;', TypeError)
verificar_error('entero x = (1 < 2) + 3;', TypeError)''')
    texto('''## 7. Validación de condiciones y ciclos

Las condiciones exigen booleano. Se recorren los bloques una vez, sin evaluar
condiciones ni ejecutar ciclos. La tabla es global: se registran incluso las
declaraciones de bloques cuya condición aparenta ser falsa.''')
    codigo('''sem = validar('entero x = 0; mientras (x < 3) { x = x + 1; }')[2]
assert sem.tabla_simbolos == {'x': 'entero'}
print('Ciclo validado sin ejecutarse:', sem.tabla_simbolos)
verificar_error('si (3) {}', TypeError)
verificar_error('mientras (1) {}', TypeError)
verificar_error('si (1 > 2) { imprimir ausente; }', NameError)''')
    texto('''## 8. Extensión personal: operador módulo

`%` conserva `OP_MODULO`, la precedencia de producto y el nodo `OpBinaria`.
Se amplía únicamente el conjunto aritmético semántico: entero × entero → entero.
No se calcula el residuo ni se comprueban divisores cero en esta entrega.''')
    codigo('''tokens, ast, sem = validar(fuente_modulo)
assert any(t.tipo == 'OP_MODULO' and t.valor == '%' for t in tokens)
assert ast.sentencias[2].valor.operador == '%'
print('Extensión preservada:', sem.tabla_simbolos)
verificar_error('entero residuo = (1 < 2) % 3;', TypeError)
verificar_error('entero residuo = 3 % (1 < 2);', TypeError)''')
    texto('''## 9. Ejemplos válidos

Los cinco programas siguientes conservan la sintaxis de entregas anteriores.
Se comprueba todo el flujo sin calcular resultados.''')
    codigo('''for prefijo in ('01_', '02_', '03_', '07_', '13_'):
    archivo = next((raiz / 'pruebas').glob(prefijo + '*.txt'))
    _, _, resultado = validar(archivo.read_text(encoding='utf-8'))
    print(archivo.name, '→', resultado.tabla_simbolos)''')
    texto('''## 10. Ejemplos inválidos

Se comprueban excepciones de nombres y tipos. No se fabrican cadenas ni decimales
que la gramática no reconoce. Las comparaciones encadenadas sin paréntesis son
error de sintaxis en el parser propio; con paréntesis se pueden probar operandos
booleanos en semántica. Es una diferencia documentada frente a una prueba docente.''')
    codigo('''for prefijo, clase in [('08_', NameError), ('09_', NameError), ('10_', NameError),
                       ('11_', TypeError), ('12_', TypeError), ('14_', TypeError),
                       ('15_', NameError), ('16_', TypeError)]:
    archivo = next((raiz / 'pruebas').glob(prefijo + '*.txt'))
    print(archivo.name)
    verificar_error(archivo.read_text(encoding='utf-8'), clase)
verificar_error('si (1 < 3 < 5) {}', SyntaxError)
verificar_error('si ((1 < 3) < 5) {}', TypeError)''')
    texto('''## 11. Pruebas automatizadas

La suite incluye las siete pruebas originales sin modificaciones y las nuevas
pruebas semánticas. Se muestran los resultados reales y se exige éxito completo.''')
    codigo('''import io
import unittest
registro = io.StringIO()
suite = unittest.defaultTestLoader.discover(str(raiz / 'pruebas'), pattern='test_*.py')
resultado = unittest.TextTestRunner(stream=registro, verbosity=1).run(suite)
print(registro.getvalue())
assert resultado.wasSuccessful()
assert not resultado.skipped
print('Pruebas:', resultado.testsRun, 'Fallos:', len(resultado.failures),
      'Errores:', len(resultado.errors), 'Omitidas:', len(resultado.skipped))''')
    texto('''## 12. Resultados y conclusiones

El recorrido propaga tipos y valida nombres, conserva las extensiones y usa una
tabla global conforme al docente. Las salidas anteriores sustentan los resultados;
el siguiente resumen se calcula desde la ejecución de la suite.

Límites: sin intérprete, TAC, ámbitos locales, análisis de inicialización ni
evaluación de divisores. Solo se conserva el primer error. Para estudiar la
implementación consultar [la guía técnica](../docs/06_GUIA_ANALISIS_SEMANTICO.md)
y [el guion de exposición](../docs/08_GUION_EXPOSICION_SEMANTICA.md).''')
    codigo('''print(f'Resultado verificado: {resultado.testsRun} pruebas, '
      f'{len(resultado.failures)} fallos y {len(resultado.errors)} errores.')
print('Módulo y tabla global comprobados con los módulos reales del proyecto.')''')
    nbf.validate(nb)
    NotebookClient(nb, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(RAIZ)}}).execute()
    nbf.validate(nb)
    destino = RAIZ / 'notebooks/05_Analisis_Semantico.ipynb'
    nbf.write(nb, destino)
    html, _ = HTMLExporter(template_name='lab').from_notebook_node(nb)
    # El HTML vive dos niveles bajo la raíz; el notebook, solo uno.
    html = html.replace('href="../docs/', 'href="../../docs/')
    (RAIZ / 'evidencias/semantico/notebook_semantico.html').write_text(html, encoding='utf-8')
    celdas_codigo = [celda for celda in nb.cells if celda.cell_type == 'code']
    assert [celda.execution_count for celda in celdas_codigo] == list(range(1, 13))
    assert all(salida.output_type != 'error' for celda in celdas_codigo for salida in celda.outputs)
    resumen = ('Notebook validado con nbformat.\n'
               '24 celdas; 12 de código ejecutadas en orden (1 a 12).\n'
               'Sin salidas de error.\nÚltima salida:\n'
               + ''.join(salida.get('text', '') for salida in celdas_codigo[-1].outputs))
    (RAIZ / 'evidencias/semantico/notebook_validacion.txt').write_text(resumen, encoding='utf-8')
    print(f'Notebook ejecutado: {len(nb.cells)} celdas; '
          f'{sum(c.cell_type == "code" for c in nb.cells)} de código.')


if __name__ == '__main__':
    preparar()
