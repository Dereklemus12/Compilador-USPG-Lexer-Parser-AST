# MiCompilador: Lexer + Parser + AST

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