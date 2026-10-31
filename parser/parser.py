from arbol_ast.nodos import (Programa, Declaracion, Asignacion, Numero,
                             Identificador, OpBinaria, Si, Mientras, Imprimir)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    @property
    def actual(self):
        return self.tokens[self.pos]

    def avanzar(self):
        token = self.actual
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def coincidir(self, tipo, valor=None):
        token = self.actual
        if token.tipo != tipo or (valor is not None and token.valor != valor):
            esperado = f"{tipo} {valor}" if valor else tipo
            raise SyntaxError(f"Línea {token.linea}, columna {token.columna}: esperado {esperado}; recibido {token.tipo} {token.valor!r}")
        self.avanzar()
        return token

    def parsear(self):
        sentencias = []
        while self.actual.tipo != 'EOF':
            sentencias.append(self.sentencia())
        self.coincidir('EOF')
        return Programa(sentencias)

    analizar = parsear

    def sentencia(self):
        tipo = self.actual.tipo
        if tipo == 'PR_ENTERO': return self.declaracion()
        if tipo == 'ID': return self.asignacion()
        if tipo == 'PR_IMPRIMIR': return self.imprimir()
        if tipo == 'PR_SI': return self.si()
        if tipo == 'PR_MIENTRAS': return self.mientras()
        raise SyntaxError(f"Línea {self.actual.linea}: sentencia inesperada {self.actual.valor!r}")

    def declaracion(self):
        self.coincidir('PR_ENTERO')
        nombre = self.coincidir('ID').valor
        valor = None
        if self.actual.tipo == 'OP_ASIG':
            self.avanzar()
            valor = self.expresion()
        self.coincidir('PUNTO_COMA')
        return Declaracion(nombre, valor)

    def asignacion(self):
        nombre = self.coincidir('ID').valor
        self.coincidir('OP_ASIG')
        valor = self.expresion()
        self.coincidir('PUNTO_COMA')
        return Asignacion(nombre, valor)

    def imprimir(self):
        self.coincidir('PR_IMPRIMIR')
        expresion = self.expresion()
        self.coincidir('PUNTO_COMA')
        return Imprimir(expresion)

    def si(self):
        self.coincidir('PR_SI')
        self.coincidir('PAR_IZQ')
        condicion = self.expresion()
        self.coincidir('PAR_DER')
        return Si(condicion, self.bloque())

    def mientras(self):
        self.coincidir('PR_MIENTRAS')
        self.coincidir('PAR_IZQ')
        condicion = self.expresion()
        self.coincidir('PAR_DER')
        return Mientras(condicion, self.bloque())

    def bloque(self):
        self.coincidir('LLAVE_IZQ')
        instrucciones = []
        while self.actual.tipo not in ('LLAVE_DER', 'EOF'):
            instrucciones.append(self.sentencia())
        self.coincidir('LLAVE_DER')
        return instrucciones

    def expresion(self):
        izquierda = self.suma()
        if self.actual.tipo == 'OP_REL':
            op = self.avanzar().valor
            izquierda = OpBinaria(izquierda, op, self.suma())
        return izquierda

    def suma(self):
        izquierda = self.producto()
        while self.actual.tipo == 'OP_ARIT' and self.actual.valor in ('+', '-'):
            op = self.avanzar().valor
            izquierda = OpBinaria(izquierda, op, self.producto())
        return izquierda

    def producto(self):
        izquierda = self.unario()
        while self.actual.tipo == 'OP_ARIT' and self.actual.valor in ('*', '/'):
            op = self.avanzar().valor
            izquierda = OpBinaria(izquierda, op, self.unario())
        return izquierda

    def unario(self):
        if self.actual.tipo == 'OP_ARIT' and self.actual.valor == '-':
            self.avanzar()
            return OpBinaria(Numero(0), '-', self.unario())
        return self.primario()

    def primario(self):
        tipo = self.actual.tipo
        if tipo == 'NUMERO': return Numero(int(self.avanzar().valor))
        if tipo == 'ID': return Identificador(self.avanzar().valor)
        if tipo == 'PAR_IZQ':
            self.avanzar()
            expresion = self.expresion()
            self.coincidir('PAR_DER')
            return expresion
        raise SyntaxError(f"Línea {self.actual.linea}: se esperaba número, identificador o expresión entre paréntesis")
