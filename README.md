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
