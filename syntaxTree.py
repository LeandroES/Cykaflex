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
    return result_dict

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

def buscar_nodo_por_id(root, target_id):
    if root.id == target_id:
        return root
    for child in root.children:
        result = buscar_nodo_por_id(child, target_id)
        if result is not None:
            return result
    return None

def parse_ll1(lexer, tabla_sintactica):
    try:
        while stack[-1].symbol != '$':
            stack_symbol = stack[-1]
            input_symbol = input[0]["symbol"]
            if stack_symbol.symbol == input_symbol:
                stack.pop()
                input.pop(0)
            else:
                production = tabla[(stack_symbol.symbol, input_symbol)]
                if production != 'e':
                    node_f = stack.pop()
                    for symbol in reversed(production.split()):
                        node_stackX = node_stack(symbol, None)
                        stack.append(node_stackX)
                        node_treeX = node_tree(node_stackX.id, node_stackX.symbol, node_stackX.lexeme)
                        node_father = buscar_nodo_por_id(root, node_f.id)
                        node_father.children.append(node_treeX)
                        node_treeX.father = node_father
                else:
                    node_f = stack.pop()
                    node_stackX = node_stack('e', None)
                    node_treeX = node_tree(node_stackX.id, node_stackX.symbol, node_stackX.lexeme)
                    node_father = buscar_nodo_por_id(root, node_f.id)
                    node_father.children.append(node_treeX)
                    node_treeX.father = node_father
    except Exception as e:
        print(str(e))

def print_tree(node, level=0, prefix="Root"):
    """Recursively prints the tree."""
    if node is not None:
        indent = " " * (level * 4)  # Ajusta el nivel de indentación
        print(f"{indent}{prefix} -> ID: {node.id}, Symbol: {node.symbol}, Lexeme: '{node.lexeme}'")
        for child in node.children:
            print_tree(child, level + 1, f"Child of ID {node.id}")

# Llamada inicial para imprimir el árbol desde la raíz
print_tree(root)
