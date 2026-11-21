# Guía técnica y demostración de la entrega final

## Recorrido del compilador

`main.py` lee el archivo fuente y ejecuta, en orden, Lexer, Parser, análisis
semántico, generación TAC y máquina virtual. Las opciones `--solo-lexer`,
`--solo-parser`, `--solo-semantica` y `--solo-tac` permiten inspeccionar una
fase sin ejecutar las posteriores. La función pública `compilar(codigo)` sigue
devolviendo `(tokens, AST)` para conservar compatibilidad con las entregas
anteriores; `validar(codigo)` devuelve `(tokens, AST, analizador_semantico)`.

## Generador TAC

`GeneradorTAC` despacha los nodos por tipo (`generar_Programa`,
`generar_Declaracion`, `generar_Asignacion`, `generar_Imprimir`, `generar_Si` y
`generar_Mientras`). `evaluar_expr` devuelve literales y nombres de variables;
para cada `OpBinaria` visita primero sus operandos, crea un temporal y emite la
operación correspondiente. De este modo `%` se conserva como operación del AST
y se convierte directamente en una instrucción TAC.

Las instrucciones tienen la forma `(op, arg1, arg2, res)`. Las condiciones se
expresan mediante operaciones relacionales que producen `1` o `0`. `si` usa
`JMP_FALSE` y una etiqueta de salida. `mientras` marca el inicio antes de
generar su condición, salta a la salida si resulta falsa, emite el cuerpo y
regresa al inicio. Así la condición se calcula en cada iteración.

Una declaración `entero x;` no genera una asignación artificial: si el programa
intenta leer `x` antes de asignarla, la VM informa que no tiene valor. Esta
decisión conserva la sintaxis semánticamente aceptada por las fases anteriores
y hace visible el error durante la ejecución.

## Máquina virtual

La VM inicializa memoria, `ip`, la lista de resultados y el mapa de etiquetas.
Cada salto ubica el puntero en el `LABEL` destino; el avance normal del ciclo
entra a la instrucción siguiente. Las operaciones aritméticas y relacionales
escriben su resultado en `res`. Las comparaciones producen enteros `1` y `0`.
La división entera usa `//`; tanto división como módulo comprueban que el
divisor no sea cero. El límite configurable de pasos detiene ciclos sin fin.

## Extensión personal y errores

El operador `%` ya formaba parte del lexer, parser, AST y semántica del proyecto.
El generador TAC emite `%` y la VM lo ejecuta con enteros, por lo que la
extensión llega desde el fuente hasta el resultado. La semántica sigue
rechazando expresiones como `(1 < 2) % 3`; la VM informa el error de ejecución
para `10 % 0`.

## Guion de demostración

Desde la raíz, ejecuta:

```powershell
python main.py pruebas/17_modulo_personal.txt
python main.py pruebas/03_control.txt
python main.py pruebas/04_error_falta_punto_coma.txt
python main.py pruebas/16_error_modulo_booleano.txt
python main.py pruebas/18_error_modulo_cero.txt
python -m unittest discover -s pruebas -p "test_*.py" -v
```

Los tres comandos intermedios terminan con código `1` intencionalmente: uno
demuestra error sintáctico, otro error semántico y el último error de
ejecución. Las transcripciones y resultados se encuentran en
[`../evidencias/final/resultados_pruebas_y_ejecucion.md`](../evidencias/final/resultados_pruebas_y_ejecucion.md).

## Límites documentados

- Solo existe el tipo `entero`; una comparación produce `booleano` para la
  validación semántica y `0` o `1` al ejecutarse.
- Las variables tienen alcance global y la semántica no comprueba
  inicialización definida.
- El parser admite una comparación relacional por expresión; no implementa
  `sino`, cadenas, decimales ni cortocircuito booleano.
- La VM ejecuta un programa en enteros; un valor no inicializado, una etiqueta
  inválida, un operador no soportado o el exceso del límite de pasos se informa
  como error en vez de producir un resultado silencioso.
