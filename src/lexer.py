import ply.lex as lex
import re

reserved = {
    'PROGRAM' : 'PROGRAM',
    'END' : 'END',
    'INTEGER' : 'INTEGER',
    'REAL' : 'REAL',
    'LOGICAL' : 'LOGICAL',
    'IF' : 'IF',
    'THEN' : 'THEN',
    'ELSE' : 'ELSE',
    'ENDIF' : 'ENDIF',
    'DO' : 'DO',
    'CONTINUE' : 'CONTINUE',
    'GOTO' : 'GOTO',
    'READ' : 'READ',
    'PRINT' : 'PRINT',
    'FUNCTION' : 'FUNCTION',
    'SUBROUTINE' :'SUBROUTINE',
    'CALL' : 'CALL',
    'RETURN' : 'RETURN',
}

tokens = ['ID', 'NEWLINE',
    'INT', 'REALNUM', 'STRING',
    'TRUE', 'FALSE', 'EQ', 'NE',
    'LT', 'LE', 'GT', 'GE', 'AND',
    'OR', 'NOT', 'POW'
] + list(reserved.values())

literals = "+-*/=(),"

t_TRUE = r'\.[Tt][Rr][Uu][Ee]\.'
t_FALSE = r'\.[Ff][Aa][Ll][Ss][Ee]\.'

t_EQ = r'\.[Ee][Qq]\.'
t_NE = r'\.[Nn][Ee]\.'
t_LT = r'\.[Ll][Tt]\.'
t_LE = r'\.[Ll][Ee]\.'
t_GT = r'\.[Gg][Tt]\.'
t_GE = r'\.[Gg][Ee]\.'

t_AND = r'\.[Aa][Nn][Dd]\.'
t_OR = r'\.[Oo][Rr]\.'
t_NOT = r'\.[Nn][Oo][Tt]\.'

t_POW = r'\*\*'

t_ignore_COMMENT = r'![^\n]*'

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    t.type = reserved.get(t.value,'ID')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_REALNUM(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'[^'\n]*'"
    t.value = t.value[1:-1]     
    return t


t_ignore = ' \t'

def t_error(t):
    print(f"illegal character {t.value[0]} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Teste: só corre quando executamos este ficheiro diretamente
if __name__ == '__main__':
    lexer.input("fat = 1\nx = 3.14 ** 2\nprint *, 'Ola, Mundo!', fat\nif (n.eq.0 .and. .not. ok) goto 10\nisprim = .true.\n")
    for tok in lexer:
        print(tok)
