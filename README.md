# Compilador USPG: del código fuente a la máquina virtual

Proyecto académico en Python que integra análisis léxico, sintáctico, AST,
semántica, generación de código de tres direcciones (TAC) y ejecución en una
máquina virtual. La entrega conserva las fases y la extensión personal `%` del
repositorio [Compilador-USPG-Lexer-Parser-AST](https://github.com/Dereklemus12/Compilador-USPG-Lexer-Parser-AST).

## Requisitos

- Python 3.10 o posterior.
- No se necesitan paquetes externos.

Ejecuta los comandos desde la raíz del proyecto.

## Ejecución

```powershell
python main.py
python main.py pruebas/17_modulo_personal.txt
python main.py pruebas/03_control.txt
python main.py pruebas/17_modulo_personal.txt --solo-tac
python main.py pruebas/03_control.txt --limite-pasos 100
```

La ejecución completa imprime los tokens, el AST, la tabla de símbolos, las
instrucciones TAC y las salidas de la VM. Para detener el proceso después de
cualquier fase:

```powershell
python main.py pruebas/17_modulo_personal.txt --solo-lexer
python main.py pruebas/17_modulo_personal.txt --solo-parser
python main.py pruebas/17_modulo_personal.txt --solo-semantica
python main.py pruebas/17_modulo_personal.txt --solo-tac
```

Un error de análisis, semántica o ejecución se imprime en consola y termina con
código de salida `1`. `--limite-pasos` evita que un ciclo infinito bloquee la
ejecución.

## Fases implementadas

1. **Lexer** (`lexer/lexer.py`): reconoce palabras reservadas, identificadores,
   enteros, operadores, delimitadores, `%` y errores léxicos con ubicación.
2. **Parser** (`parser/parser.py`): valida declaraciones, asignaciones,
   impresión, expresiones, `si` y `mientras`; conserva precedencia y negación
   unaria.
3. **AST** (`arbol_ast/nodos.py`): representa programas, sentencias,
   identificadores, literales y expresiones binarias.
4. **Semántica** (`semantic/analizador.py`): administra la tabla global de
   símbolos y verifica declaraciones, nombres, tipos y condiciones.
5. **TAC** (`intermediate/tac.py`): genera operaciones, asignaciones, impresión,
   etiquetas y saltos desde el AST ya validado.
6. **Máquina virtual** (`vm/maquina_virtual.py`): interpreta TAC, realiza
   aritmética y comparaciones, ejecuta saltos y devuelve las salidas.

Los cambios de esta entrega añaden TAC, VM, pruebas de ejecución y la integración
del pipeline en `main.py`; el lexer, parser, AST y analizador semántico previos
se conservan.

## Extensión personal: operador módulo `%`

La extensión viaja por todas las fases: el lexer produce `OP_MODULO`, el parser
lo representa como `OpBinaria`, la semántica exige operandos enteros y devuelve
`entero`, TAC emite `%` y la VM calcula el residuo. Un divisor cero se informa
durante la ejecución.

Entrada de [`pruebas/17_modulo_personal.txt`](pruebas/17_modulo_personal.txt):

```text
entero numero = 10;
entero divisor = 3;
entero residuo = numero % divisor;
si (residuo == 1) {
    imprimir residuo;
}
```

TAC generado:

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

Salida de la máquina virtual:

```text
>> SALIDA: 1
Salidas VM: [1]
```

El caso de error personal está en [`pruebas/18_error_modulo_cero.txt`](pruebas/18_error_modulo_cero.txt).
El caso semánticamente inválido `16_error_modulo_booleano.txt` comprueba que no
se acepte módulo con un operando booleano.

## Pruebas

Ejecuta la suite completa con:

```powershell
python -m unittest discover -s pruebas -p "test_*.py" -v
```

Los casos de entrada existentes cubren lexer, parser, AST y semántica. La nueva
suite `pruebas/test_tac_vm.py` comprueba operaciones y comparaciones, módulo,
asignaciones, impresión, `si`, `mientras`, saltos, etiquetas, lectura de una
variable sin inicializar, división y módulo entre cero, límite de pasos y los
puntos de corte del pipeline de consola. La ejecución documentada reportó 58
pruebas correctas, sin fallos ni errores.

| Caso | Resultado esperado | Archivo o prueba |
|---|---|---|
| Expresiones y cálculo | Válido; imprime el resultado | `pruebas/02_expresiones.txt` |
| Control y ciclos | Válido; ejecuta condiciones y ciclos | `pruebas/03_control.txt` |
| Punto y coma faltante | Error sintáctico | `pruebas/04_error_falta_punto_coma.txt` |
| Variable inexistente | Error semántico | `pruebas/08_error_variable_no_declarada.txt` |
| `%` con enteros | Válido; imprime `1` | `pruebas/17_modulo_personal.txt` |
| `%` con operando booleano | Error semántico | `pruebas/16_error_modulo_booleano.txt` |
| `%` con divisor cero | Error de ejecución | `pruebas/18_error_modulo_cero.txt` |

Las transcripciones reproducibles se guardan en `evidencias/final/` y la guía
técnica está en [`docs/10_GUIA_EJECUCION_ENTREGA_FINAL.md`](docs/10_GUIA_EJECUCION_ENTREGA_FINAL.md).

## Formato TAC y límites del lenguaje

Cada instrucción es una tupla `(operación, argumento1, argumento2, destino)`.
Los temporales `@tN` y etiquetas `@LN` son internos. `LABEL` marca destinos;
`JMP` y `JMP_FALSE` controlan el flujo. Las comparaciones producen `1` o `0`, y
la división entre enteros usa división entera de Python (`//`).

Las declaraciones sin inicializador se conservan: la semántica valida el tipo,
pero la VM informa si se intenta leer su valor antes de asignarlo. El alcance de
variables es global; el parser permite una comparación relacional por
expresión; el lenguaje no implementa `sino`, cadenas ni decimales.
