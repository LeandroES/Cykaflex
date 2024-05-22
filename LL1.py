import pandas as pd


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


tabla = pd.read_csv("tabla.csv", index_col=0)
count = 0
stack = []

# init stack
symbol_E = node_stack('E', None)
symbol_dollar = node_stack('$', None)
stack.append(symbol_dollar)
stack.append(symbol_E)

# init tree
root = node_tree(symbol_E.id, symbol_E.symbol, symbol_E.lexeme)

input = [
    {
        "symbol": "int",
        "lexeme": "4",
        "nroline": 2,
        "col": 2
    },
    {
        "symbol": "*",
        "lexeme": "*",
        "nroline": 2,
        "col": 4
    },
    {
        "symbol": "int",
        "lexeme": "5",
        "nroline": 2,
        "col": 6
    },
    {
        "symbol": "$",
        "lexeme": "$",
        "nroline": 0,
        "col": 0
    },
]

production = tabla.loc[stack[-1].symbol, input[0]["symbol"]]
print(production)
# reemplazar production (T X) en stack
# pop de stack
node_p = stack.pop()
# push de X y luego T en stack
node_X = node_stack("X", "X")  #OPE_SUM
node_T = node_stack("T", "T")
stack.append(node_X)
stack.append(node_T)

# crear los hijo X y T de E
#node_X_tree = node_tree(node_X.id, node_X.symbol, node_X.lexeme)
#node_T_tree = node_tree(node_T.id, node_T.symbol, node_T.lexeme)
#node_father = buscar_node(node_p.id)
#node_father.children.append(node_X_tree)
#node_father.children.append(node_T_tree)
#node_X_tree.father = node_father
#node_T_tree.father = node_father

