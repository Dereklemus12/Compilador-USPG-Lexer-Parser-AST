# MiCompilador: Lexer + Parser + AST

> Versión actual: [Entrega 3 — análisis semántico](#entrega-3-análisis-semántico-continuación).
> El bloque inicial conserva la documentación histórica de las entregas anteriores.

Implementación autónoma de referencia, adaptada desde el lexer original del estudiante. **No es una edición del `parser/parser.py` del docente**, pues ese archivo no se pudo descargar para comprobar la compatibilidad de sus firmas y TODO.

## Ejecución

Desde la raíz, con Python 3.10+:

```powershell
python main.py pruebas/01_basico_valido.txt
python -m unittest discover -s pruebas -p "test_*.py" -v
```

## Arquitectura

- `lexer/lexer_original.py`: copia íntegra del lexer entregado.
- `lexer/lexer.py`: adaptación del lexer del estudiante, manteniendo los tokens originales, añadiendo EOF y errores explícitos.
- `parser/parser.py`: parser descendente recursivo (NO LR(0)).
- `arbol_ast/nodos.py`: nodos AST mediante dataclasses.
- `notebooks/`: documentación y ejercicio LR(0), independiente del parser principal.

Esta entrega **no incluye** semántica ni ejecución de código fuente.

## Evidencias de ejecución

El proyecto incluye cuatro Jupyter Notebooks:

1. Construcción de la colección LR(0), ACTION/GOTO y análisis de abb.
2. Reconocimiento léxico y generación de tokens.
3. Integración del parser y construcción del AST.
4. Pruebas de integración y detección de errores.

Las salidas ejecutadas se almacenan en
`evidencias/notebooks_ejecutados/`.

## Extensión del analizador léxico

Se conserva el lexer original de la primera entrega.

Adicionalmente, se incorpora el operador módulo `%`
como token `OP_MODULO`.

El parser reconoce este operador con la misma
precedencia que multiplicación y división.

Ejemplo:

    entero residuo = 10 % 3;

La extensión se verifica mediante
`test_operador_modulo` y el archivo
`07_token_personalizado.txt`.

## Pruebas

Para ejecutar las pruebas automatizadas:

    python -m unittest discover -s pruebas -p "test_*.py" -v

La entrega no incluye análisis semántico
ni ejecución de instrucciones.

---

## Entrega 3: análisis semántico (continuación)

Las secciones anteriores se conservan como historia de la entrega Lexer + Parser
+ AST. La versión actual añade validación semántica; continúa sin ejecutar
instrucciones ni generar TAC.

**Código → Lexer → Tokens → Parser → AST → Analizador semántico → Validación.**

Se integró la [plantilla del docente](https://github.com/ciarenasg-uspg/compilador-entrega-semantica/blob/5fc51c0a3de764118b43cf6fac5645f730dde6b5/semantic/analizador.py)
conservando el lexer, parser, AST y extensiones personales existentes.
Se mantienen los contratos anteriores y se añaden propiedades de compatibilidad
a los nodos AST. `compilar(codigo)` sigue devolviendo tokens y AST;
`validar(codigo)` añade el resultado semántico.

### Los seis métodos de la entrega

| Método | Validación |
|---|---|
| visitar_Declaracion | Duplicados, inicializador y registro del tipo |
| visitar_Asignacion | Existencia y compatibilidad de tipos |
| visitar_Identificador | Existencia; devuelve el tipo registrado |
| visitar_OpBinaria | Operandos enteros; tipo aritmético o booleano; extensión `%` |
| visitar_Si | Condición booleana y bloque |
| visitar_Mientras | Condición booleana y bloque, sin ejecutar el ciclo |

La plantilla consultada contiene cinco TODO literales: el visitante binario ya
está resuelto, aunque el README del docente enumera seis pendientes. Se completan
los cinco y se amplía el sexto método enumerado, sin inventar responsabilidades.

### Tipos, símbolos y errores

Solo hay declaraciones `entero`. Los operadores `+ - * / %` reciben enteros y
devuelven entero. Las comparaciones `== != < > <= >=` reciben enteros y devuelven
booleano. Las condiciones exigen booleano; las asignaciones e inicializadores
deben coincidir con el tipo de la variable. `imprimir` valida su expresión.

La tabla es un diccionario global `{nombre: tipo}`. La presencia de una clave
indica declaración; no guarda valores ni estado de inicialización. Se conserva
`entero x;`. No hay ámbitos locales: todos los bloques comparten la tabla.
Los errores de nombres usan `NameError` con línea, y los de tipos `TypeError`.
El análisis termina en el primer error; la consola muestra la tabla parcial.

El operador personal `%` conserva token, precedencia y nodo. Un caso válido
está en [07_token_personalizado.txt](pruebas/07_token_personalizado.txt);
el [caso inválido](pruebas/16_error_modulo_booleano.txt) usa `(1 < 2) % 3`.
La negación unaria y los paréntesis reutilizan las reglas existentes.

### Ejecutar y reproducir evidencias

```powershell
python main.py pruebas/07_token_personalizado.txt
python main.py pruebas/16_error_modulo_booleano.txt
python main.py --solo-parser pruebas/16_error_modulo_booleano.txt
python -m unittest discover -s pruebas -p "test_*.py" -v
python pruebas/generar_evidencias_semantico.py
```

Resultado verificado con Python 3.13.1: **41 pruebas (7 anteriores + 34 nuevas),
0 fallos, 0 errores y 0 omisiones**. También se verificaron 16 programas por
consola: cinco válidos y once rechazos esperados. Las salidas reales están en
[evidencias/semantico/](evidencias/semantico/), incluida la
[evolución de la tabla](evidencias/semantico/evolucion_tabla_simbolos.txt).

### Material de estudio y presentación

- [Guía técnica, procedencia y reglas](docs/06_GUIA_ANALISIS_SEMANTICO.md).
- [Guía de ejecución y reproducción](docs/07_GUIA_EJECUCION_ENTREGA_SEMANTICA.md).
- [Guion de exposición](docs/08_GUION_EXPOSICION_SEMANTICA.md).
- [Bitácora de procedimientos realizados](docs/09_BITACORA_PROCEDIMIENTOS_ENTREGA_SEMANTICA.md):
  auditoría, decisiones, implementación, comandos, pruebas y publicación en GitHub.
- [Notebook de análisis semántico](notebooks/05_Analisis_Semantico.ipynb), con
  importaciones reales, ejemplos, tabla, errores y suite de pruebas.

### Limitaciones

No se evalúan expresiones, divisores cero, condiciones o ciclos. No hay TAC,
intérprete, variables booleanas, cadenas, decimales ni análisis de inicialización.
Las comparaciones encadenadas sin paréntesis siguen siendo error de sintaxis
en este parser; se documenta la diferencia con la prueba remota del docente.
Las expresiones booleanas entre paréntesis permiten probar incompatibilidades
reales sin ampliar la gramática. No se afirma compatibilidad de constructores
con todo AST externo: se conservan los constructores propios del proyecto.
