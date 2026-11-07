# Guion de exposición: entrega semántica

## 1. Objetivo y continuidad

«Continué el mismo compilador. Conservo los tokens, el parser, los nodos y las
siete pruebas anteriores. Después del AST agregué un visitante que comprueba
declaraciones y tipos, sin ejecutar el programa».

Mostrar la arquitectura y distinguir: `@` causa error léxico; `entero x = ;`
causa error sintáctico; `imprimir desconocida;` tiene sintaxis válida pero falla
en semántica. Ejecutar el caso 10 para mostrar el último.

## 2. Recorrido Visitor y seis responsabilidades

Abrir `semantic/analizador.py`. Explicar cómo `analizar` elige el método según
la clase AST. Señalar declaración, asignación, identificador, operación binaria,
condicional y ciclo. Aclarar con honestidad que la cuarta responsabilidad ya
tenía código en la plantilla consultada y se amplió para la extensión personal.

«Una expresión devuelve su tipo, no su resultado. Un literal devuelve entero;
una comparación devuelve booleano. Una sentencia valida sus componentes».

## 3. Tabla global

Ejecutar `python main.py pruebas/07_token_personalizado.txt` y abrir
`evidencias/semantico/evolucion_tabla_simbolos.txt`. Mostrar el crecimiento de
la tabla. Su clave es el nombre y su valor es el tipo. La presencia indica que
la variable está declarada. No guarda valores calculados ni inicialización.

«Registro después de comprobar el inicializador; por eso `entero x = x + 1;`
falla. Una variable en un bloque pertenece a la misma tabla global. Es la
simplificación del docente, no un sistema de ámbitos locales».

## 4. Tipos y módulo

Mostrar `OP_MODULO`, la regla `producto` del parser, el nodo `OpBinaria` y la
inclusión de `%` entre los aritméticos del visitante.

«Dos enteros producen entero. `(1 < 2) % 3` falla porque el primer operando
es booleano. Esto se puede escribir con la gramática existente».

Ejecutar el caso 16 y después el 11. Explicar que solo se declaran enteros,
pero las comparaciones sí producen un segundo tipo; por eso hay incompatibilidades
representables sin añadir cadenas o decimales.

## 5. Condiciones y ciclos

Ejecutar los casos 12 y 13. Mostrar que una condición debe ser booleana y que
el visitante inspecciona el cuerpo una vez. No toma decisiones ni repite el
ciclo; incluso un cuerpo bajo condición falsa se comprueba.

## 6. Evidencias y cierre

Ejecutar `python -m unittest discover -s pruebas -p "test_*.py" -v`.
Mostrar el notebook ejecutado y las evidencias reproducibles. Resultado registrado:
41 pruebas, cero fallos, cero errores y cero omisiones. Hay 16 verificaciones
de consola con códigos de salida comprobados.

Preguntas previsibles:

- ¿Es un intérprete? No; solo propaga tipos y valida nombres.
- ¿Calcula `10 % 3`? No; concluye que tiene tipo entero.
- ¿Detecta divisor cero? No en esta entrega; no evalúa expresiones.
- ¿Permite `entero x;`? Sí, extensión ya existente; la plantilla no controla inicialización.
- ¿Acepta `1 < x < 5`? El parser propio lo rechaza; `(1 < x) < 5` llega a semántica y falla por tipos.
- ¿Se completaron seis TODO literales? Se atendieron los seis métodos enumerados
  por el docente; el archivo remoto tenía cinco TODO y uno ya resuelto.

No afirmar generación de TAC, ejecución de instrucciones ni análisis de flujo
que el proyecto no realiza.
