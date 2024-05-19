import csv
import ply.lex as lex
import pandas as pd

tokens = (

    'RIGHT_KEY',
    'LEFT_KEY',
    'RIGHT_BRACKET',
    'LEFT_BRACKET',
    'CONTENT',
    'TEXTO',
    'CENTIMETER',
    'POINT',
    'NUMBER',
    'ITEM',
    'INICIO',
    'FIN',
    'DOCUMENTO',
    'TITULOPAGINA',
    'INICIOE',
    'INICIOI',
    'ENUMERAR',
    'ITEMIZAR',
    'NEGRITA',
    'CURSIVA',
    'SECCION',
    'SUBSECCION',
    'SUBSUBSECCION',
    'CHAPTER',
    'NEWPAGE',
    'DOCUMENTCLASS',
    'ARTICLE',
    'BOOK',
    'COMMENT'

)

# Regular expression rules for simple tokens
t_RIGHT_KEY = r'\}'
t_LEFT_KEY = r'\{'
t_RIGHT_BRACKET = r'\]'
t_LEFT_BRACKET = r'\['
t_CONTENT = r'".+"'
t_TEXTO = r'texto'
t_CENTIMETER = r'cm'
t_POINT = r'pt'
t_NUMBER = r'[0-9]+'
t_ITEM = r'item'
t_INICIO = r'inicio'
t_FIN = r'fin'
t_DOCUMENTO = r'documento'
t_TITULOPAGINA = r'titulopagina'
t_INICIOE = r'inicioe'
t_INICIOI = r'inicioi'
t_ENUMERAR = r'ennumerar'
t_ITEMIZAR = r'itemizar'
t_NEGRITA = r'negrita'
t_CURSIVA = r'cursiva'
t_SECCION = r'seccion'
t_SUBSECCION = r'subseccion'
t_SUBSUBSECCION = r'subsubseccion'
t_CHAPTER = r'capitulo'
t_NEWPAGE = r'nuevapagina'
t_DOCUMENTCLASS = r'clasedocumento'
t_ARTICLE = r'articulo'
t_BOOK = r'libro'
t_COMMENT = r'%.+'

entrada = []


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test it out
with open('Example_1.txt', 'r') as file:
    data = file.read()


def leer_gramatica(a):
    with open(a, 'r') as a:
        reglas = {}
        for linea in a:
            partes = linea.strip().split('->')
            izquierda = partes[0].strip()
            derecha = [simbolo.strip().split() for simbolo in partes[1].split('|')]
            reglas[izquierda] = derecha
        return reglas


def es_no_terminal(simbolo):
    return simbolo.islower()


def calcular_tabla_sintactica(reglas, conjuntos_primeros, conjuntos_siguientes):
    tabla = {no_terminal: {} for no_terminal in reglas}

    for no_terminal, producciones in reglas.items():
        for produccion in producciones:
            primeros_produccion = set()
            puede_ser_vacia = False
            for simbolo in produccion:
                if es_no_terminal(simbolo):
                    primeros_produccion.update(conjuntos_primeros[simbolo])
                    if '' in conjuntos_primeros[simbolo]:
                        puede_ser_vacia = True
                        continue
                    else:
                        break
                else:
                    primeros_produccion.add(simbolo)
                    break

            # Añadir siempre los siguientes para ver si el problema está en el condicional
            produccion_info = {
                'produccion': produccion,
                'primeros': {terminal for terminal in primeros_produccion if terminal},
                'siguientes': conjuntos_siguientes[no_terminal]
            }

            for terminal in primeros_produccion:
                if terminal != '':
                    tabla[no_terminal][terminal] = produccion_info

    return tabla

def calcular_conjuntos_primeros(reglas):
    conjuntos_primeros = {clave: set() for clave in reglas}
    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in reglas.items():
            for produccion in producciones:
                produccion_vacia = True
                for simbolo in produccion:
                    if simbolo == "''":
                        conjuntos_primeros[no_terminal].add('')
                    elif es_no_terminal(simbolo):
                        cuenta_actual = len(conjuntos_primeros[no_terminal])
                        conjuntos_primeros[no_terminal].update(conjuntos_primeros[simbolo] - {''})
                        if '' not in conjuntos_primeros[simbolo]:
                            produccion_vacia = False
                        if cuenta_actual != len(conjuntos_primeros[no_terminal]):
                            cambio = True
                    else:
                        cuenta_actual = len(conjuntos_primeros[no_terminal])
                        conjuntos_primeros[no_terminal].add(simbolo)
                        produccion_vacia = False
                        if cuenta_actual != len(conjuntos_primeros[no_terminal]):
                            cambio = True
                    if not produccion_vacia:
                        break
                if produccion_vacia:
                    if '' not in conjuntos_primeros[no_terminal]:
                        conjuntos_primeros[no_terminal].add('')
                        cambio = True
    return conjuntos_primeros


def calcular_conjuntos_siguientes(reglas, conjuntos_primeros):
    conjuntos_siguientes = {clave: set() for clave in reglas}
    conjuntos_siguientes['documento'].add('$')

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in reglas.items():
            for produccion in producciones:
                for i in range(len(produccion)):
                    actual = produccion[i]
                    if es_no_terminal(actual):
                        siguiente_conjunto = set()
                        # Caso cuando hay símbolos después del actual en la producción
                        if i + 1 < len(produccion):
                            siguiente = produccion[i + 1]
                            if es_no_terminal(siguiente):
                                siguiente_conjunto.update(conjuntos_primeros[siguiente] - {''})
                                if '' in conjuntos_primeros[siguiente]:
                                    siguiente_conjunto.update(conjuntos_siguientes[no_terminal])
                            else:
                                siguiente_conjunto.add(siguiente)
                        else:
                            # Caso cuando el actual es el último en la producción
                            siguiente_conjunto.update(conjuntos_siguientes[no_terminal])

                        # Actualizar conjuntos de "siguientes" del no terminal actual
                        if siguiente_conjunto:
                            antes = len(conjuntos_siguientes[actual])
                            conjuntos_siguientes[actual].update(siguiente_conjunto)
                            if antes != len(conjuntos_siguientes[actual]):
                                cambio = True

    return conjuntos_siguientes


def exportar_tabla_a_csv(tabla, nombre_archivo):
    with open(nombre_archivo, 'w', newline='') as csvfile:
        fieldnames = ['Primeros', 'Siguientes', 'No Terminal', 'Terminal', 'Produccion']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for no_terminal, terminales in tabla.items():
            for terminal, info in terminales.items():
                # Asegurar que la producción se convierte correctamente a string
                produccion_str = ' '.join(info['produccion'])
                # Asegurar que los conjuntos de primeros y siguientes son convertidos a string y separados por comas
                primeros_str = ', '.join(info['primeros'])
                siguientes_str = ', '.join(info['siguientes'])

                writer.writerow({
                    'Primeros': primeros_str,
                    'Siguientes': siguientes_str,
                    'No Terminal': no_terminal,
                    'Terminal': terminal,
                    'Produccion': produccion_str
                })

def imprimir_tabla_sintactica(tabla):
    print("Tabla Sintáctica LL(1):")
    for no_terminal, producciones in tabla.items():
        print(f'"{no_terminal}":')
        for terminal, produccion in producciones.items():
            print(f'    "{terminal}": {produccion}')
    print()

def imprimir_conjuntos_primeros(conjuntos_primeros):
    print("Conjuntos de Primeros:")
    for no_terminal, conjunto_primero in conjuntos_primeros.items():
        print(f'"{no_terminal}": {list(conjunto_primero)}')
    print()


def imprimir_conjuntos_siguientes(conjuntos_siguientes):
    print("Conjuntos de Siguientes:")
    for no_terminal, conjunto_siguiente in conjuntos_siguientes.items():
        print(f'"{no_terminal}": {list(conjunto_siguiente)}')
    print()

def parse_ll1(lexer, tabla_sintactica):
    stack = ['$', 'DOCUMENTO']
    token = lexer.token()
    try:
        while stack:
            top = stack.pop()
            current_input = token.type if token else '$'
            if top in tokens:
                if top == current_input:
                    token = lexer.token()
                else:
                    raise Exception('Error de sintaxis')
            else:
                regla = tabla_sintactica[top].get(current_input)
                if regla:
                    for symbol in reversed(regla):
                        if symbol != 'epsilon':
                            stack.append(symbol)
                else:
                    raise Exception('Error de sintaxis')
    except Exception as e:
        print(str(e))


def cargar_tabla_sintactica(filename):
    df = pd.read_csv(filename)
    tabla = {}
    for _, row in df.iterrows():
        no_terminal = row['No Terminal']
        terminal = row['Terminal']
        produccion = row['Produccion'].split()
        if no_terminal not in tabla:
            tabla[no_terminal] = {}
        tabla[no_terminal][terminal] = produccion
    return tabla



def main():
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok.type, tok.value, tok.lineno, tok.lexpos)
    print('\n')
    archivo                 = 'input.txt'
    reglas                  =   leer_gramatica(archivo)
    conjuntos_primeros      =   calcular_conjuntos_primeros(reglas)
    conjuntos_siguientes    =   calcular_conjuntos_siguientes(reglas, conjuntos_primeros)
    tabla_sintactica        =   calcular_tabla_sintactica(reglas, conjuntos_primeros, conjuntos_siguientes)

    imprimir_conjuntos_primeros(conjuntos_primeros)
    imprimir_conjuntos_siguientes(conjuntos_siguientes)
    imprimir_tabla_sintactica(tabla_sintactica)

    exportar_tabla_a_csv(tabla_sintactica, 'tabla_sintactica.csv')
    tabla_sintactica = cargar_tabla_sintactica('tabla_sintactica.csv')
    parse_ll1(lexer, tabla_sintactica)
main()
