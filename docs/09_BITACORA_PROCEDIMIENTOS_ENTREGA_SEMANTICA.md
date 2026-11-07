# Bitácora de procedimientos: entrega de análisis semántico

Fecha de elaboración: 6 de noviembre de 2026.

Este documento registra el trabajo realizado para continuar el compilador USPG:
qué se inspeccionó, cómo se integró la plantilla, qué decisiones se tomaron,
cómo se verificaron los resultados y cómo se publicó la entrega. Es una memoria
técnica del procedimiento, no una transcripción literal del chat.

## 1. Estado publicado y punto de partida

**La implementación ya está subida a GitHub. No hace falta publicarla otra vez.**

- Repositorio: [Compilador-USPG-Lexer-Parser-AST](https://github.com/Dereklemus12/Compilador-USPG-Lexer-Parser-AST).
- Rama de publicación: `main`.
- Commit previo: `d5cbfdd`, integración del operador módulo y evidencias anteriores.
- Commit de la entrega semántica: [`626ce89b1b91ee8cbb12f8c03b976503f29cc30b`](https://github.com/Dereklemus12/Compilador-USPG-Lexer-Parser-AST/commit/626ce89b1b91ee8cbb12f8c03b976503f29cc30b).
- Mensaje: `Entrega 3: analisis semantico, tabla de simbolos y pruebas`.
- Resultado de publicación: `git push origin main` terminó correctamente y avanzó
  el remoto de `d5cbfdd` a `626ce89`.
- La comprobación posterior mostró el directorio de trabajo limpio y los mismos
  identificadores en `HEAD` y `origin/main`.

Esta bitácora se redactó después de ese commit; su incorporación se registra
en un commit documental posterior. No forma parte del contenido de `626ce89`.

## 2. Procedimiento de auditoría inicial

### 2.1. Confirmar el repositorio antes de modificarlo

Se ejecutaron las siguientes consultas desde la raíz del proyecto principal:

```powershell
git rev-parse --show-toplevel
git remote -v
git status --short --branch
git branch -a
git log -5 --oneline
```

Se comprobó que el remoto era el repositorio del estudiante, la rama era `main`
y no había modificaciones pendientes. No se trabajó sobre la copia histórica.

### 2.2. Revisar la implementación y sus interfaces

Se enumeraron los archivos con `rg --files` y se leyeron el programa principal,
lexer, tokens, parser, nodos AST, pruebas de integración, README y evidencias.
También se revisó el material de los notebooks anteriores.

Los puntos de entrada encontrados fueron:

| Componente | Contrato existente |
|---|---|
| Lexer | `Lexer(codigo).analizar()` devuelve tokens y termina con EOF |
| Parser | `Parser(tokens).parsear()` devuelve un `Programa` |
| Programa principal | `compilar(codigo)` devuelve `(tokens, ast)` |
| AST | Dataclasses con nombres propios como `nombre`, `valor`, `izquierda` y `cuerpo` |

El proyecto tenía siete pruebas de integración, cuatro notebooks y la extensión
`OP_MODULO` para `%`. El parser ya admitía declaraciones sin inicializador y
negación unaria. No existía la carpeta semántica y la carpeta de guías estaba vacía.

### 2.3. Buscar la plantilla antes de implementar

Se buscó `analizador.py` en los archivos disponibles de la carpeta de Compiladores
y se revisó el árbol de archivos de la referencia local de `origin/main`.
Al no encontrarlo, se informó la falta y se detuvo la implementación semántica.
No se inventaron seis métodos basándose únicamente en categorías generales.

## 3. Localización y lectura de la plantilla del docente

Después de recibir los enlaces del docente, se consultaron ambos repositorios:

- [Entrega de parser](https://github.com/ciarenasg-uspg/compilador-entrega-parser):
  corresponde a la fase anterior, sin análisis semántico.
- [Entrega de semántica](https://github.com/ciarenasg-uspg/compilador-entrega-semantica):
  contiene la plantilla, instrucciones, nodos de referencia y pruebas semánticas.

Se utilizó la API de GitHub para consultar el árbol de archivos y leer los blobs
de la plantilla, README, AST, programa principal, pruebas y guía de extensiones.
La consulta web inicial de semántica no devolvió contenido; la API permitió leerlo.

Referencia fijada para poder verificar el origen:

```text
Commit del docente: 5fc51c0a3de764118b43cf6fac5645f730dde6b5
Archivo: semantic/analizador.py
Blob Git: aff5707f2ee6c6e6657d8db0a11dc8cf1c1797ea
```

[Consultar la plantilla exacta](https://github.com/ciarenasg-uspg/compilador-entrega-semantica/blob/5fc51c0a3de764118b43cf6fac5645f730dde6b5/semantic/analizador.py).

Se identificó una discrepancia entre instrucciones y archivo: el README enumera
seis métodos TODO, pero el archivo tiene cinco pendientes, numerados 1, 2, 3, 5 y 6.
El visitante binario ya contiene las reglas base. Por tanto, se completaron los
cinco pendientes y se amplió ese visitante para `%`. Esta diferencia quedó
explicada en las guías, README y notebook.

## 4. Procedimiento de implementación incremental

### 4.1. Adaptar las interfaces conservando el AST propio

Se mantuvieron las clases y los argumentos posicionales anteriores. Se añadió
la base `NodoAST` y propiedades de lectura para los nombres esperados por la plantilla:

| Nodo | Compatibilidad añadida |
|---|---|
| Declaracion | `id` consulta `nombre`; `expr` consulta `valor`; `tipo` es `entero` |
| Asignacion | `id` consulta `nombre`; `expr` consulta `valor` |
| OpBinaria | `izq`, `op`, `der` consultan `izquierda`, `operador`, `derecha` |
| Imprimir | `expr` consulta `expresion` |
| Si | `bloque_v` consulta `cuerpo` |
| Mientras | `bloque` consulta `cuerpo` |

Se incorporó la línea de origen en declaraciones, asignaciones e identificadores.
El parser la obtiene del token correspondiente. Ese campo se excluyó de la
representación y comparación de dataclasses para conservar el comportamiento previo.

### 4.2. Completar los visitantes semánticos

Se creó [semantic/analizador.py](../semantic/analizador.py) con los nombres y firmas
del docente. Se conservó el despacho Visitor mediante `analizar(nodo)`.

| Método | Procedimiento aplicado |
|---|---|
| `visitar_Declaracion` | Comprobar duplicados, analizar el inicializador cuando existe, comparar su tipo y registrar al final |
| `visitar_Asignacion` | Comprobar que exista la variable y comparar el tipo de la expresión con el guardado |
| `visitar_Identificador` | Buscar el nombre y devolver el tipo; informar `NameError` con línea cuando falta |
| `visitar_OpBinaria` | Analizar ambos operandos, exigir enteros e inferir el tipo del resultado; añadir `%` |
| `visitar_Si` | Exigir condición booleana y recorrer el bloque |
| `visitar_Mientras` | Exigir condición booleana y recorrer el bloque una sola vez, sin ejecutar el ciclo |

El registro de declaraciones ocurre después de validar el inicializador.
Así, `entero x = x + 1;` detecta que `x` todavía no existe y una declaración
con inicializador inválido no queda incorporada a la tabla.

### 4.3. Aplicar las reglas reales del docente

La tabla se mantuvo como un diccionario global `{nombre: tipo}`. No se añadieron
ámbitos locales ni valores de ejecución. Solo se declaran variables `entero`;
las comparaciones producen `booleano`.

```text
+ - * / %              entero, entero -> entero
== != < > <= >=        entero, entero -> booleano
si / mientras         condición de tipo booleano
declarar / asignar    expresión del mismo tipo que la variable
```

Se conservó `entero x;` porque ya existía en la sintaxis propia. La plantilla
no exige comprobar si una variable está inicializada; por eso no se incorporó
ese estado a la tabla ni se agregó un análisis de flujo.

### 4.4. Conservar y validar la extensión personal

La ruta de `%` quedó así:

```text
Texto % -> token OP_MODULO -> producto() -> OpBinaria -> visitar_OpBinaria
```

El lexer y la precedencia del parser ya lo admitían. El cambio semántico consistió
en incluirlo en el conjunto aritmético. `numero % divisor` es válido con enteros;
`(1 < 2) % 3` se rechaza porque la comparación produce booleano.

No fue necesario crear un nodo de módulo ni otro visitante. El negativo unario
y los paréntesis reutilizan las reglas anteriores.

### 4.5. Integrar el flujo principal

En [main.py](../main.py) se conservó `compilar(codigo) -> (tokens, ast)` y se agregó
`validar(codigo) -> (tokens, ast, semantico)`. La consola muestra tokens, AST,
resultado semántico y tabla. Ante un error semántico muestra la tabla parcial
y devuelve código de salida 1; una ejecución válida devuelve 0.

Se añadieron los modos `--solo-lexer` y `--solo-parser` para inspeccionar las fases
sin exigir que las siguientes sean válidas.

## 5. Procedimiento de pruebas y generación de evidencias

### 5.1. Mantener las pruebas anteriores

Se ejecutaron las siete pruebas iniciales y se mantuvo su archivo sin modificar.
Las nuevas comprobaciones se añadieron en
[test_semantico.py](../pruebas/test_semantico.py), utilizando assertions sobre
tipos, tabla, excepciones, líneas y códigos de salida.

### 5.2. Ejecutar la suite completa

Comando reproducible desde la raíz:

```powershell
python -m unittest discover -s pruebas -p "test_*.py" -v
```

Resultado registrado con Python 3.13.1:

| Comprobación | Resultado |
|---|---:|
| Pruebas anteriores | 7 |
| Pruebas nuevas | 34 |
| Total ejecutado | 41 |
| Fallos | 0 |
| Errores | 0 |
| Omitidas | 0 |

Se cubrieron duplicados, identificadores inexistentes, autorreferencia,
incompatibilidades, operadores, condiciones, bloques, alcance global, `%`,
negación unaria y comportamiento de la consola.

### 5.3. Verificar programas completos y guardar salidas reales

Se creó [generar_evidencias_semantico.py](../pruebas/generar_evidencias_semantico.py).
Este script ejecuta la suite, lanza los programas mediante procesos Python,
comprueba los códigos de salida y guarda sus salidas. Se ejecutó con:

```powershell
python pruebas/generar_evidencias_semantico.py
```

Se verificaron los archivos 01 a 16: cinco válidos y once rechazos esperados,
de los cuales dos son sintácticos y nueve semánticos. También se registró cómo
cambia la tabla al visitar cada sentencia del programa de módulo.

Referencias a las salidas auténticas:

- [Detalle de las 41 pruebas](../evidencias/semantico/pruebas_completas.txt).
- [Resumen de comprobaciones](../evidencias/semantico/resumen.txt).
- [Evolución de símbolos](../evidencias/semantico/evolucion_tabla_simbolos.txt).
- [Programa válido con módulo](../evidencias/semantico/07_token_personalizado.txt).
- [Rechazo del módulo con booleano](../evidencias/semantico/16_error_modulo_booleano.txt).

### 5.4. Documentar diferencias sin ocultar fallos

Una prueba remota del docente espera error semántico para `1 < x < 5`.
La gramática propia ya rechaza esa construcción con `SyntaxError`, al admitir
una comparación por expresión. Se conservó la gramática y se comprobó ese
comportamiento. Con paréntesis, `(1 < x) < 5` sí llega a semántica y se rechaza
porque intenta comparar un booleano con un entero.

No se afirma que la suite remota completa se ejecutara y aprobara sin adaptaciones.
Las 41 pruebas reportadas son la suite integrada del proyecto.

## 6. Procedimiento del notebook académico

Se creó [05_Analisis_Semantico.ipynb](../notebooks/05_Analisis_Semantico.ipynb)
con las doce secciones solicitadas, importaciones del proyecto, ejemplos válidos
e inválidos, traza de símbolos y ejecución de las pruebas.

Se configuró Python y se utilizó el intérprete instalado de Python 3.13.1.
La instalación inicial mediante la herramienta de paquetes no dejó `nbformat`
disponible en ese intérprete; se comprobó el error de importación y se corrigió
instalando las dependencias explícitamente para el intérprete seleccionado.

Los comandos portables equivalentes son:

```powershell
python -m pip install -r notebooks/requirements.txt
python notebooks/preparar_semantico.py
```

El [script de preparación](../notebooks/preparar_semantico.py):

1. Construye el notebook con `nbformat` y valida su estructura.
2. Ejecuta las celdas con `nbclient` en un kernel nuevo.
3. Guarda el notebook con sus resultados reales.
4. Genera una vista HTML con `nbconvert`.
5. Comprueba orden de ejecución y ausencia de salidas de error.
6. Escribe un archivo de validación reproducible.

Se ejecutaron doce celdas de código, numeradas del 1 al 12, dentro de un total
de 24 celdas. No hubo salidas de error. La suite volvió a aprobar dentro del
notebook. Se abrió la representación HTML, se revisaron sus doce secciones
y salidas, y se comprobó ausencia de desbordamiento horizontal en esa ventana.

La herramienta del editor no llegó a seleccionar un kernel, pero la ejecución
sí se completó mediante `nbclient`. Por tanto, las salidas guardadas proceden
de esa ejecución y no de una selección de kernel en la interfaz del editor.

Ver [validación guardada](../evidencias/semantico/notebook_validacion.txt).

## 7. Documentación y revisión final

Se amplió el [README](../README.md) conservando la historia anterior y se crearon:

- [Guía técnica](06_GUIA_ANALISIS_SEMANTICO.md): procedencia, seis métodos,
  compatibilidad, reglas, símbolos y limitaciones.
- [Guía de ejecución](07_GUIA_EJECUCION_ENTREGA_SEMANTICA.md): comandos,
  resultados esperados y reproducción del notebook y evidencias.
- [Guion de exposición](08_GUION_EXPOSICION_SEMANTICA.md): demostraciones
  y respuestas para presentar la implementación.

Se amplió [.gitignore](../.gitignore) para excluir entornos, temporales,
configuración local de herramientas y archivos `.env`.

Antes de publicar se revisaron el diff, los archivos nuevos, las evidencias y
patrones habituales de credenciales. No se detectaron coincidencias en la búsqueda
realizada. La herramienta de diagnósticos del editor no informó errores.
Las comprobaciones de espacios de Git terminaron sin incidencias.

```powershell
git diff --check
git diff --stat
git status --short
git diff --cached --check
git diff --cached --stat
```

La entrega de implementación contiene 45 archivos nuevos o modificados.
El inventario se puede consultar en el commit publicado y en la guía técnica.
El lexer, los tokens, las pruebas iniciales, los casos 01 a 07 y los cuatro
notebooks históricos se conservaron sin editar.

## 8. Procedimiento de publicación en GitHub

Se prepararon explícitamente los archivos pertinentes con `git add --` seguido
de sus rutas; no se añadió indiscriminadamente todo el directorio. Después de
revisar lo preparado, se ejecutó:

```powershell
git commit -m "Entrega 3: analisis semantico, tabla de simbolos y pruebas"
git push origin main
git status --short --branch
git rev-parse HEAD origin/main
```

El entorno restringido impidió inicialmente escribir el índice de Git.
Se solicitó el permiso de ejecución correspondiente y se completaron la preparación,
el commit y el push. No se cambió el remoto, no se utilizó `--force` y no se
eliminó historial.

El push respondió:

```text
d5cbfdd..626ce89  main -> main
```

La verificación posterior devolvió el mismo hash completo para `HEAD` y
`origin/main`, y un estado limpio. Esta comprobación se refiere al cierre de
la entrega semántica; los commits documentales posteriores tendrán otro hash.

## 9. Qué puedes repetir para estudiar el procedimiento

Desde la raíz, con el intérprete de Python del proyecto:

```powershell
# Observar un programa válido y su tabla.
python main.py pruebas/07_token_personalizado.txt

# Observar un error semántico representable.
python main.py pruebas/16_error_modulo_booleano.txt

# Comprobar que ese mismo programa sí tiene sintaxis válida.
python main.py --solo-parser pruebas/16_error_modulo_booleano.txt

# Comprobar toda la suite y regenerar evidencias.
python -m unittest discover -s pruebas -p "test_*.py" -v
python pruebas/generar_evidencias_semantico.py

# Regenerar y ejecutar el notebook, con sus dependencias instaladas.
python notebooks/preparar_semantico.py
```

Los comandos de reproducción pueden actualizar tiempos de prueba, metadatos
y salidas de los archivos de evidencia. Eso no significa que haya un cambio
de reglas del compilador. No hace falta crear otro commit ni hacer push para
estudiar los ejemplos localmente.

## 10. Límites que deben conservarse al explicar el trabajo

El compilador valida nombres y tipos. No calcula valores, no ejecuta `imprimir`,
no decide ramas, no repite ciclos y no genera TAC ni código ejecutable.
No hay ámbitos locales, variables booleanas declarables, cadenas, decimales,
análisis de inicialización ni comprobación de divisores cero. El análisis
se detiene en el primer error.

Las restricciones anteriores son límites documentados de esta etapa académica.
No deben presentarse como funcionalidades implementadas o pruebas pendientes
de características que la gramática actual no permite representar.
