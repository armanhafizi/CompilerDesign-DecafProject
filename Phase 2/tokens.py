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
]