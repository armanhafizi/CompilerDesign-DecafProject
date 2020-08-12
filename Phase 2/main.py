import sys
import getopt
import ply.lex as lex
import csv
import re
from collections import namedtuple
import reserved as r
import tokens as t


reserved = r.reserved
tokens = t.tokens + list(reserved.values())  # List of token names.   This is always required


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
file = open('ParseTable.csv', 'r')
dataReader = csv.reader(file, delimiter=';')
data = []
for row in dataReader:
    data.append(row)
parse_table = {}
row = data[0]
s1 = row[0].split(',')
s2 = row[1].split(',')
inputs = s1
inputs[-1] = ';'
for i in range(1, len(s2)):
    inputs.append(s2[i])
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
        t = inputs[j]
        if t == 'intConstant':
            parse_table[cell(state=num, input='T_INTLITERAL')] = table[i][j]
        elif t == 'doubleConstant':
            parse_table[cell(state=num, input='T_DOUBLELITERAL')] = table[i][j]
        elif t == 'stringConstant':
            parse_table[cell(state=num, input='T_STRINGLITERAL')] = table[i][j]
        elif t == 'boolConstant':
            parse_table[cell(state=num, input='T_BOOLEANLITERAL')] = table[i][j]
        elif t == 'ident':
            parse_table[cell(state=num, input='T_ID')] = table[i][j]
        elif t == 'print':
            parse_table[cell(state=num, input='Print')] = table[i][j]
        elif t == 'readLine':
            parse_table[cell(state=num, input='ReadLine')] = table[i][j]
        elif t == '~':
            parse_table[cell(state=num, input=',')] = table[i][j]
        elif t == '^^':
            parse_table[cell(state=num, input='||')] = table[i][j]
        else:
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
    state_stack = [0]
    parse_stack = [1]
    has_errors = False  # the output of the parser
    tok = lexer.token()
    while True:
        if not tok:
            break  # No more input
        if tok.type == "T_UNDEFINED_TOKEN":
            has_errors = True
            break
        if tok.type in show_token:
            token = tok.type
            # this if and else should be changed but don't know how yet
            data_token += '{} {}\n'.format(tok.type, tok.value)
        else:
            token = tok.value
            data_token += '{}\n'.format(tok.value)

        # parser code based on token
        top = state_stack[-1]
        action = get_action(parse_table[cell(state=top, input=token)])
        num = get_num(parse_table[cell(state=top, input=token)])
        if action == 'ERROR':
            has_errors = True
            break
        elif action == 'SHIFT':
            state_stack.append(num)
            tok = lexer.token()
            parse_stack[-1] += 1
        elif action == 'ACCEPT':
            break
        elif action == 'REDUCE':
            number_of_pops = parse_stack.pop()
            for i in range(number_of_pops):
                state_stack.pop()
            next_state = get_num(PT_cell=parse_table[cell(state= state_stack[-1],input=num)])
            state_stack.append(next_state)
            parse_stack[-1] += 1
        elif action == 'PUSH':
            state_stack.append(num)
            parse_stack.append(1)

    output = 'YES'  # TODO : Bug in Document
    if has_errors:
        output = 'No'  # TODO : Bug in Document
    with open("tests/" + outputfile, "w") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    main(sys.argv[1:])
