# Resultados de pruebas y evidencia de ejecución

Validación realizada con Python 3.13.1 desde la raíz del repositorio.

## Pruebas automatizadas

Comando:

```powershell
python -m unittest discover -s pruebas -p "test_*.py" -v
```

Resultado:

```text
Ran 58 tests
OK
```

Las 58 pruebas incluyen las siete de integración existentes, las pruebas de
semántica y 17 casos nuevos de TAC/VM y CLI. La ejecución terminó sin fallos, errores
ni advertencias.

## Caso válido: operador personal `%`

Comando: `python main.py pruebas/17_modulo_personal.txt`

Resultado de la tabla semántica:

```text
Análisis semántico correcto.
{'divisor': 'entero', 'numero': 'entero', 'residuo': 'entero'}
```

TAC:

```text
('ASSIGN', '10', None, 'numero')
('ASSIGN', '3', None, 'divisor')
('%', 'numero', 'divisor', '@t1')
('ASSIGN', '@t1', None, 'residuo')
('==', 'residuo', '1', '@t2')
('JMP_FALSE', '@t2', None, '@L1')
('PRINT', 'residuo', None, None)
('LABEL', None, None, '@L1')
```

Salida de la VM:

```text
>> SALIDA: 1
Salidas VM: [1]
```

## Caso válido: ciclo `mientras` con condición recalculada

Comando: `python main.py pruebas/03_control.txt`

El TAC coloca la etiqueta del ciclo antes de la comparación y vuelve a esa
etiqueta después del cuerpo. La salida observada fue:

```text
>> SALIDA: 1
Salidas VM: [1]
```

El ejemplo imprime `x` solamente cuando `x == 1`, dentro de tres iteraciones.

## Errores esperados

| Comando | Fase que lo detecta | Resultado observado | Código de salida |
|---|---|---|---:|
| `python main.py pruebas/04_error_falta_punto_coma.txt` | Parser | `Línea 2, columna 1: esperado PUNTO_COMA; recibido PR_IMPRIMIR 'imprimir'` | 1 |
| `python main.py pruebas/16_error_modulo_booleano.txt` | Semántica | `Operador '%' exige dos enteros, se recibieron 'booleano' y 'entero'.` | 1 |
| `python main.py pruebas/18_error_modulo_cero.txt` | VM | `[Error VM] Módulo entre cero.` | 1 |

Los códigos `1` son los resultados esperados para casos negativos; no son fallos
de la suite automatizada. Los casos de error semántico y ejecución muestran la
tabla parcial disponible al momento en que se detiene el compilador.

## Extensión personal

El caso `pruebas/17_modulo_personal.txt` confirma la ruta completa de `%`:
`OP_MODULO` en el Lexer, `OpBinaria` en el AST, validación de enteros en
semántica, instrucción `%` en TAC y cálculo de residuo en la VM. El caso de
error `pruebas/18_error_modulo_cero.txt` verifica el divisor cero en la fase de
ejecución; `pruebas/16_error_modulo_booleano.txt` verifica operandos
incompatibles en semántica.
