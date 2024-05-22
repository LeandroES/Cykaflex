import csv
import main

main.main()
input = main.lexico()

class node_stack:

  def __init__(self, symbol, lexeme):
    global count
    self.symbol = symbol
    self.lexeme = lexeme
    self.id = count + 1
    count += 1

class node_tree:

  def __init__(self, id, symbol, lexeme):
    self.id = id
    self.symbol = symbol
    self.lexeme = lexeme
    self.children = []
    self.father = None

def csv_to_dict(file_path):
    result_dict = {}

    with open(file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) < 3:
                continue  # Skips rows that don't have at least 3 columns
            key = (row[0], row[1])
            value = row[2]
            result_dict[key] = value
    #print(result_dict)
    return result_dict



#tabla = pd.read_csv("tabla.csv", index_col=0)
count = 0
stack = []

# init stack
symbol_E = node_stack('documento', None)
symbol_dollar = node_stack('$', None)
stack.append(symbol_dollar)
stack.append(symbol_E)

# init tree
root = node_tree(symbol_E.id, symbol_E.symbol, symbol_E.lexeme)

tabla = csv_to_dict("tabla_sintactica.csv")

#key_to_check = ('clave1_col1', 'clave2_col2')

production = tabla['documento', 'DOCUMENTCLASS']

print(production)


def parse_ll1(lexer, tabla_sintactica):
    try:
        while stack[-1].symbol != '$':
            top = stack.pop()
            current_input = input[0]["type"]
            if top in main.tokens:
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

#parse_ll1(lexer, tabla_sintactica)

