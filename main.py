import csv

import pandas as pd
import ply.lex as lex

tokens = (
    "RIGHT_KEY",
    "LEFT_KEY",
    "RIGHT_BRACKET",
    "LEFT_BRACKET",
    "CONTENT",
    "TEXTO",
    "CENTIMETER",
    "POINT",
    "NUMBER",
    "ITEM",
    "INICIO",
    "FIN",
    "DOCUMENTO",
    "TITULOPAGINA",
    "INICIOE",
    "INICIOI",
    "ENUMERAR",
    "ITEMIZAR",
    "NEGRITA",
    "CURSIVA",
    "SECCION",
    "SUBSECCION",
    "SUBSUBSECCION",
    "CHAPTER",
    "NEWPAGE",
    "DOCUMENTCLASS",
    "ARTICLE",
    "BOOK",
    "COMMENT",
)

# Regular expression rules for simple tokens
t_RIGHT_KEY = r"\}"
t_LEFT_KEY = r"\{"
t_RIGHT_BRACKET = r"\]"
t_LEFT_BRACKET = r"\["
t_CONTENT = r'".+"'
t_TEXTO = r"texto"
t_CENTIMETER = r"cm"
t_POINT = r"pt"
t_NUMBER = r"[0-9]+"
t_ITEM = r"item"
t_INICIO = r"inicio"
t_FIN = r"fin"
t_DOCUMENTO = r"documento"
t_TITULOPAGINA = r"titulopagina"
t_INICIOE = r"inicioe"
t_INICIOI = r"inicioi"
t_ENUMERAR = r"ennumerar"
t_ITEMIZAR = r"itemizar"
t_NEGRITA = r"negrita"
t_CURSIVA = r"cursiva"
t_SECCION = r"seccion"
t_SUBSECCION = r"subseccion"
t_SUBSUBSECCION = r"subsubseccion"
t_CHAPTER = r"capitulo"
t_NEWPAGE = r"nuevapagina"
t_DOCUMENTCLASS = r"clasedocumento"
t_ARTICLE = r"articulo"
t_BOOK = r"libro"
t_COMMENT = r"%.+"

entrada = []


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test it out
with open("Example_1.txt", "r") as file:
    data = file.read()


def leer_gramatica(a):
    with open(a, "r") as a:
        reglas = {}
        for linea in a:
            partes = linea.strip().split("->")
            izquierda = partes[0].strip()
            derecha = [simbolo.strip().split() for simbolo in partes[1].split("|")]
            reglas[izquierda] = derecha
        return reglas


def es_no_terminal(simbolo):
    return simbolo.islower()


##experimental


def calcular_tabla_sintactica(reglas, conjuntos_primeros, conjuntos_siguientes):
    tabla = {no_terminal: {} for no_terminal in reglas}

    for no_terminal, producciones in reglas.items():
        for produccion in producciones:
            primeros_produccion = set()
            puede_ser_vacia = False

            # Calcular el conjunto de primeros para la producción actual
            for simbolo in produccion:
                if es_no_terminal(simbolo):
                    primeros_produccion.update(conjuntos_primeros[simbolo])
                    if "e" in conjuntos_primeros[simbolo]:
                        puede_ser_vacia = True
                        continue
                    else:
                        break
                else:
                    primeros_produccion.add(simbolo)
                    break

            if puede_ser_vacia:
                primeros_produccion.add("e")

            produccion_info = {
                "produccion": produccion if produccion != [""] else ["e"],
                "primeros": {terminal for terminal in primeros_produccion if terminal},
                "siguientes": conjuntos_siguientes[no_terminal],
            }

            for terminal in primeros_produccion:
                tabla[no_terminal][terminal] = produccion_info

            if puede_ser_vacia:
                for terminal in conjuntos_siguientes[no_terminal]:
                    tabla[no_terminal][terminal] = produccion_info
    #print('Tabla: ', tabla)
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
                        conjuntos_primeros[no_terminal].add(
                            "e"
                        )  # Aquí se maneja la producción vacía
                    elif es_no_terminal(simbolo):
                        cuenta_actual = len(conjuntos_primeros[no_terminal])
                        conjuntos_primeros[no_terminal].update(
                            conjuntos_primeros[simbolo] - {"e"}
                        )
                        if "e" not in conjuntos_primeros[simbolo]:
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
                    if "e" not in conjuntos_primeros[no_terminal]:
                        conjuntos_primeros[no_terminal].add("e")
                        cambio = True
        print(f"First sets updated: {conjuntos_primeros}")
    return conjuntos_primeros


def calcular_conjuntos_siguientes(reglas, conjuntos_primeros):
    conjuntos_siguientes = {clave: set() for clave in reglas}
    conjuntos_siguientes["documento"].add("$")

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in reglas.items():
            for produccion in producciones:
                for i in range(len(produccion)):
                    actual = produccion[i]
                    if es_no_terminal(actual):
                        siguiente_conjunto = set()
                        if i + 1 < len(produccion):
                            siguiente = produccion[i + 1]
                            if es_no_terminal(siguiente):
                                siguiente_conjunto.update(
                                    conjuntos_primeros[siguiente] - {"e"}
                                )
                                if "e" in conjuntos_primeros[siguiente]:
                                    siguiente_conjunto.update(
                                        conjuntos_siguientes[no_terminal]
                                    )
                            else:
                                siguiente_conjunto.add(siguiente)
                        else:
                            siguiente_conjunto.update(conjuntos_siguientes[no_terminal])

                        if siguiente_conjunto:
                            antes = len(conjuntos_siguientes[actual])
                            conjuntos_siguientes[actual].update(siguiente_conjunto)
                            if antes != len(conjuntos_siguientes[actual]):
                                cambio = True
        print(f"Follow sets updated: {conjuntos_siguientes}")
    return conjuntos_siguientes


def exportar_tabla_a_csv(tabla, nombre_archivo):
    with open(nombre_archivo, "w", newline="") as csvfile:
        fieldnames = ["No Terminal", "Terminal", "Produccion"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for no_terminal, terminales in tabla.items():
            for terminal, info in terminales.items():
                produccion_str = " ".join(info["produccion"])
                if produccion_str == "''":
                    produccion_str = "e"
                writer.writerow(
                    {
                        "No Terminal": no_terminal,
                        "Terminal": terminal,
                        "Produccion": produccion_str,
                    }
                )
                # print(no_terminal, terminal, produccion_str)

        # Agregar explícitamente las producciones vacías con terminales de los conjuntos siguientes
        for no_terminal, terminales in tabla.items():
            if any("e" == info["produccion"] for info in terminales.values()):
                for siguiente in terminales:
                    if siguiente not in tabla[no_terminal]:
                        writer.writerow(
                            {
                                "No Terminal": no_terminal,
                                "Terminal": siguiente,
                                "Produccion": "e",
                            }
                        )


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


def cargar_tabla_sintactica(filename):
    df = pd.read_csv(filename)
    tabla = {}
    for _, row in df.iterrows():
        no_terminal = row["No Terminal"]
        terminal = row["Terminal"]
        produccion = row["Produccion"].split()
        if no_terminal not in tabla:
            tabla[no_terminal] = {}
        tabla[no_terminal][terminal] = produccion
    return tabla


def lexico():
    lexer.input(data)
    lex = []
    lista_tokens = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        info_token = {
            "symbol": tok.type,
            "lexeme": tok.value,
            "nroline": tok.lineno,
            "col": tok.lexpos,
        }
        lista_tokens.append(info_token)
    nuevo_token = {"symbol": "$", "lexeme": "$", "nroline": 0, "col": 0}
    lista_tokens.append(nuevo_token)
    return lista_tokens


def imprimir_ultimo_siguiente(conjuntos_siguientes):
    print("Último elemento del conjunto de Siguientes:")
    for no_terminal, conjunto_siguiente in conjuntos_siguientes.items():
        if conjunto_siguiente:
            ultimo_elemento = list(conjunto_siguiente)[-1]
            print(f'"{no_terminal}": {ultimo_elemento}')
    print()


def main():
    archivo = "input.txt"
    reglas = leer_gramatica(archivo)
    conjuntos_primeros = calcular_conjuntos_primeros(reglas)
    conjuntos_siguientes = calcular_conjuntos_siguientes(reglas, conjuntos_primeros)
    tabla_sintactica = calcular_tabla_sintactica(
        reglas, conjuntos_primeros, conjuntos_siguientes
    )

    #imprimir_conjuntos_siguientes(conjuntos_siguientes)  # Para verificación
    #imprimir_ultimo_siguiente(conjuntos_siguientes)  # Añadido para verificación
    exportar_tabla_a_csv(tabla_sintactica, "tabla_sintactica.csv")
    # tabla_sintactica = cargar_tabla_sintactica('tabla_sintactica.csv')


if __name__ == "__main__":
    main()
