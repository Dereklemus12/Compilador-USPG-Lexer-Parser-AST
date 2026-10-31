import re
from typing import List
from lexer.token import Token

# -------------------------------------------------
# Estructura de datos para un Token
# -------------------------------------------------
# -------------------------------------------------
# Clase Lexer: Analizador Léxico Completo
# -------------------------------------------------
class Lexer:
    def __init__(self, codigo: str):
        # Almacenamos el código a analizar
        self.codigo = codigo
        
        # Diccionario de Palabras Reservadas (PR)
        self.palabras_reservadas = {
            'si': 'PR_SI',
            'mientras': 'PR_MIENTRAS',
            'imprimir': 'PR_IMPRIMIR',
            'entero': 'PR_ENTERO'
        }

        # Especificación de Tokens mediante Expresiones Regulares
        self.patrones = [
            # Operadores Relacionales (OP_REL)
            ('OP_REL',      r'==|!=|<=|>=|<|>'),

            # Operador de Asignación (=)
            ('OP_ASIG',     r'='),

            # Operadores Aritméticos 
            ('OP_ARIT',     r'[\+\-\*/]'),

            # Símbolos de Estructura 
            ('PUNTO_COMA',  r';'),
            ('PAR_IZQ',     r'\('),
            ('PAR_DER',     r'\)'),
            ('LLAVE_IZQ',   r'\{'),
            ('LLAVE_DER',   r'\}'),

            # Datos Básicos
            ('NUMERO',      r'\d+'),
            ('ID',          r'[a-zA-Z_]\w*'),

            # Caracteres a ignorar y contar
            ('ESPACIOS',    r'[ \t]+'),
            ('NUEVA_LINEA', r'\n'),

            # Error Léxico (Cualquier otro carácter que no coincida)
            ('DESCONOCIDO', r'.'),
        ]

        # Compilar los patrones en una sola expresión regular maestra
        partes_regex = [f'(?P<{nombre}>{patron})' for nombre, patron in self.patrones]
        self.regex_maestra = re.compile('|'.join(partes_regex))

    # Método para iniciar el análisis léxico
    def analizar(self) -> List[Token]:
        tokens_encontrados = []
        numero_linea = 1
        inicio_linea = 0

        # Iterar sobre todas las coincidencias encontradas en el código
        for match in self.regex_maestra.finditer(self.codigo):
            tipo = match.lastgroup
            valor = match.group(tipo)
            
            # Calcular la columna exacta
            columna = match.start() - inicio_linea + 1

            if tipo == 'NUEVA_LINEA':
                # Sumar línea e indicar dónde empieza la nueva línea
                numero_linea += 1
                inicio_linea = match.end()
                continue
            elif tipo == 'ESPACIOS':
                # Ignorar espacios
                continue
            elif tipo == 'ID' and valor in self.palabras_reservadas:
                # Si el identificador es una palabra reservada, cambiar su tipo
                tipo = self.palabras_reservadas[valor]
            elif tipo == 'DESCONOCIDO':
                # Lanzar un error descriptivo si hay caracteres extraños
                raise SyntaxError(f"Error léxico: carácter inesperado {valor!r} en línea {numero_linea}, columna {columna}")

            # Crear el token y guardarlo
            tokens_encontrados.append(Token(tipo, valor, numero_linea, columna))

        tokens_encontrados.append(Token("EOF", "", numero_linea, len(self.codigo) - inicio_linea + 1))
        return tokens_encontrados