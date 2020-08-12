import sys
import getopt
import ply.lex as lex
import csv
import re
from collections import namedtuple


reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'new': 'NEW',
    'NewArray': 'NEWARRAY',
    'int': 'INT',
    'interface': 'INTERFACE',
    'bool': 'BOOL',
    'void': 'VOID',
    'return': 'RETURN',
    'break': 'BREAK',
    'class': 'CLASS',
    'double': 'DOUBLE',
    'extends': 'EXTENDS',
    'null': 'NULL',
    'Print': 'PRINT',
    'string': 'STRING',
    'implements': 'IMPLEMENTS',
    'ReadLine': 'READLINE',
    'ReadInteger': 'READInteger',
    'this': 'THIS'
}
# List of token names.   This is always required
tokens = [
    'T_ID',
    # int, double, boolean
    'T_INTLITERAL',
    'T_DOUBLELITERAL',
    'T_BOOLEANLITERAL',
    # string
    'T_STRINGLITERAL',
    # +  *  -  \  ==  !=  =
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'EQ',
    'NEQ',
    'ASSIGN',
    # < , > , <= , >=
    'LT',
    'LEQ',
    'GT',
    'GEQ',
    # ;  '.' ','
    'SEMICOLON',
    'DOT',
    'COMMA',
    # [], {}, (), %
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'PERCENT',
    # and, or, not
    'AND',
    'OR',
    'NOT',
    # ++ , --
    'INC',
    'DEC',
    # comment
    'ignore_COMMENT',
    'UNDEFINED_TOKEN',
] + list(reserved.values())


# Regular expression rules for simple tokens
t_DOT = r'\.'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_EQ = r'=='
t_NEQ = r'!='
t_ASSIGN = r'='
t_INC = r'\+\+'
t_DEC = r'--'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_PERCENT = r'%'
t_COMMA = r','
t_SEMICOLON = r';'
t_LT = r'<'
t_LEQ = r'<='
t_GT = r'>'
t_GEQ = r'>='
t_ignore_COMMENT = r'//.*'


def t_T_DOUBLELITERAL(t):
    r'\d+\.\d*((e|E)(\+|-)?\d+)?'
    t.value = t.value
    return t


def t_T_INTLITERAL(t):
    r'0[xX][0-9a-fA-F]+|\d+'
    t.value = t.value
    return t


def t_T_STRINGLITERAL(t):
    r'"([^\\"]|\\\\|\\"|\\n|\\t)*"'
    t.value = t.value[0:]
    t.lexer.lineno += t.value.count('\n')  # since newlines may be embedded in strings
    return t


def t_ID(t):
    r'[a-zA-Z][_a-zA-Z_0-9]{0,30}'
    if t.value == 'false' or t.value == 'true': # Check true and false
        t.type = 'T_BOOLEANLITERAL'
    else:
        t.type = reserved.get(t.value, 'T_ID')    # Check for reserved words
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Also through multiline comments
def t_ignore_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


def t_error(t):
    t.type = "T_UNDEFINED_TOKEN"
    t.lexer.skip(1)
    return t

# Error handling rule
# def t_error(t):
#     print('UNDEFINED_TOKEN')
#     t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


# Creating Parse Table
cell = namedtuple("cell", ["state", "input"])
file = open('PT_v2.csv', 'r')
datareader = csv.reader(file, delimiter=';')
data = []
for row in datareader:
    data.append(row)
parse_table = {}
row = data[0]
s1 = row[0].split(',')
s2 = row[1].split(',')
inputs = s1
inputs[-1] = ';'
inputs.append('|')
for i in s2:
    inputs.append(i)
table = []
for row in data:
        if len(row) > 1:
            continue
        else:
            for s in row:
                table.append(s.split(','))

for i in range(len(table)):
    num = int(table[i][0])
    for j in range(1, len(table[i])):
        parse_table[cell(state=num, input=inputs[j])] = table[i][j]


def get_action(PT_cell):
    if PT_cell.startswith('ERROR'):
        return 'ERROR'
    elif PT_cell.startswith('REDUCE'):
        return 'REDUCE'
    elif PT_cell.startswith('PUSH'):
        return 'PUSH'
    elif PT_cell.startswith('SHIFT'):
        return 'SHIFT'
    elif PT_cell.startswith('ACCEPT'):
        return 'ACCEPT'
    else:
        return 'GOTO'


def get_num(PT_cell):
    if PT_cell.startswith('REDUCE'):
        s = PT_cell.split(' ')
        return s[-1]
    if PT_cell.startswith('ERROR'):
        return -1
    if PT_cell.startswith('ACCEPT'):
        return -2
    numbers = [int(num) for num in re.findall(r"\d+", PT_cell)]
    return numbers[0]


# ending parsetable
def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    with open("tests/" + inputfile, "r") as input_file:
        data = input_file.read()

    # Tokenize
    lexer.input(data)
    show_token = ['T_ID', 'T_INTLITERAL', 'T_DOUBLELITERAL', 'T_STRINGLITERAL', 'T_BOOLEANLITERAL']
    data_token = ''
    # new part for parser
    stack = [0]
    parse_stack = []
    has_errors = False  # the output of the parser
    push_occured = False
    tok = lexer.token()
    while True:
        if not push_occured:
            tok = lexer.token()
            if not tok:
                break  # No more input
            if tok.type == "T_UNDEFINED_TOKEN":
                has_errors = True
                break
            if tok.type in show_token:
                data_token += '{} {}\n'.format(tok.type,
                                               tok.value)  # this if and else should be changed but don't know how yet
            else:
                data_token += '{}\n'.format(tok.value)
        # parser code based on  token
        top = stack[-1]
        action = get_action(parse_table[cell(state=top, input=tok.value)])  # I think tok.value should be edited
        num = get_num(parse_table[cell(state=top, input=tok.value)])
        push_occured = False
        if action == 'ERROR':
            has_errors = True
            break
        elif action == 'SHIFT':
            stack.append(num)
        elif action == 'ACCEPT':
            break
        elif action == 'REDUCE':
            number_of_pops = abs(stack.pop()-parse_stack.pop())
            for i in range(number_of_pops):
                stack.pop()
            next_state = get_num(PT_cell=parse_table[cell(state=stack[-1], input=num)])
            if num == -1: #error
                has_errors = True
                break
            elif num == -2:  # accept
                break
            # where the last 5 lines really necessary?
            stack.append(next_state)
        elif action == 'Push':
            push_occured = True
            stack.append(num)
            parse_stack.append(num)
    with open("out/" + outputfile, "w") as output_file:
        output_file.write(has_errors)

    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break  # No more input
    #     if tok.type == "T_UNDEFINED_TOKEN":
    #         data_token += '{} {}\n'.format(tok.type, tok.value)
    #         #adding no to upload fi
    #         break
    #     if tok.type in show_token:
    #             data_token += '{} {}\n'.format(tok.type, tok.value)
    #     else:
    #         data_token += '{}\n'.format(tok.value)
    #     #parser code based on  token
    #     top = stack[-1]
    #     action = get_action(parse_table[cell(state= top,input=tok.value)])
    #
    #
    # with open("out/" + outputfile, "w") as output_file:
    #     output_file.write(data_token)


if __name__ == "__main__":
    main(sys.argv[1:])