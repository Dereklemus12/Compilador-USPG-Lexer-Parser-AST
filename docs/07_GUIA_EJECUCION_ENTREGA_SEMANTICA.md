# Ejecutar y verificar la entrega semántica

Desde la raíz del repositorio, usar Python 3.10 o superior. El compilador y las
pruebas usan únicamente la biblioteca estándar.

```powershell
python main.py pruebas/01_basico_valido.txt
python main.py pruebas/07_token_personalizado.txt
python main.py pruebas/16_error_modulo_booleano.txt
python main.py --solo-lexer pruebas/07_token_personalizado.txt
python main.py --solo-parser pruebas/16_error_modulo_booleano.txt
python -m unittest discover -s pruebas -p "test_*.py" -v
python pruebas/generar_evidencias_semantico.py
```

La ejecución completa imprime tokens, AST, resultado semántico y tabla global.
Los modos parciales sirven para distinguir errores de cada fase. Un programa
sintácticamente válido puede fallar en semántica; el caso 16 lo demuestra.

## Casos de consola

| Archivos | Resultado |
|---|---|
| 01, 02, 03, 07, 13 | Válidos; salida 0 |
| 04, 05 | Errores de sintaxis; salida 1 |
| 06, 08, 10, 15 | Identificadores no declarados; salida 1 |
| 09 | Declaración duplicada; salida 1 |
| 11, 14 | Incompatibilidad booleano/entero; salida 1 |
| 12 | Condición entera; salida 1 |
| 16 | Módulo con operando booleano; salida 1 |

El generador comprueba los códigos de salida con assertions y falla si una
prueba o programa no da el resultado esperado. Escribe las salidas reales en
`evidencias/semantico/`; no copia resultados simulados. La evidencia histórica
de las entregas anteriores se conserva.

## Notebook

Abrir [05_Analisis_Semantico.ipynb](../notebooks/05_Analisis_Semantico.ipynb)
con un kernel Python y ejecutar todas las celdas en orden. Importa los módulos
reales y localiza la raíz desde la carpeta de notebooks o desde el repositorio.

Para regenerarlo y ejecutarlo automáticamente:

```powershell
python -m pip install -r notebooks/requirements.txt
python notebooks/preparar_semantico.py
```

El script usa `nbformat` para generar y validar la estructura, `nbclient` para
ejecutar todas las celdas en un kernel nuevo y `nbconvert` para generar una vista
HTML de revisión. La salida se guarda en el propio notebook. Las dependencias
Jupyter son exclusivas de la documentación; no las necesita el compilador.

## Verificación realizada

Entorno de esta entrega: Python 3.13.1 en Windows. La evidencia automatizada
incluye versión exacta, detalle de cada prueba y comandos de consola.
Se comprobaron 41 pruebas sin fallos ni errores y 16 programas por consola.
Las celdas del notebook vuelven a ejecutar la suite y exigen resultado satisfactorio.
El notebook también comprueba el módulo y la evolución de la tabla de símbolos.
Se ejecutaron sus 24 celdas, incluidas 12 de código en orden, sin salidas de error.
Se revisó la representación HTML con las doce secciones y las salidas guardadas,
sin desbordamiento horizontal en la ventana de revisión. Ver
[validación del notebook](../evidencias/semantico/notebook_validacion.txt).

No se certifican aquí otros intérpretes Python mediante una matriz de versiones.
Las reglas, límites y diferencias con el docente se explican en la
[guía técnica](06_GUIA_ANALISIS_SEMANTICO.md).
