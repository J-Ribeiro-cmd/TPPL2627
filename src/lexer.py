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

# NOVO: estado para as linhas de comentario (C, c ou * na coluna 1)
states = (
    ('comentario', 'exclusive'),
)

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

t_ignore_COMMENT = r'![^\n]*'      # comentario ! ate ao fim da linha (ja existia)

# NOVO: tem de ser a PRIMEIRA funcao (o ply testa as funcoes pela ordem do ficheiro)
# Mudanca(s) de linha seguida(s) de C, c ou * e um espaco/fim de linha = linha de comentario
def t_INICIO_COMENTARIO(t):
    r'\n+[Cc\*](?=[ \t\n])'
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('comentario')

def t_comentario_FIM(t):
    r'(?=\n)'                      # nao consome o \n: a linha seguinte pode ser outro comentario
    t.lexer.begin('INITIAL')

def t_comentario_TEXTO(t):
    r'[^\n]+'
    pass                           # descarta o texto do comentario

t_comentario_ignore = ''

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

# ALTERADO: t_ANY_error em vez de t_error, para valer tambem no estado 'comentario'
def t_ANY_error(t):
    print(f"illegal character {t.value[0]} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# NOVO: usar sempre esta funcao em vez de lexer.input(codigo)
# O '\n' inicial deixa a 1a linha ser comentario; lineno = 0 compensa esse '\n' extra
def tokenizar(codigo):
    lexer.lineno = 0
    lexer.begin('INITIAL')
    lexer.input('\n' + codigo)
    return list(lexer)

# Teste: só corre quando executamos este ficheiro diretamente
if __name__ == '__main__':
    codigo = """C     Exemplo com comentarios
      PROGRAM TESTE
      INTEGER FAT, N

* outro comentario, depois de uma linha em branco
c em minusculas tambem
      FAT = 1
      CALL TROCA(FAT, N)
      PRINT *, 'Ola ! Mundo', FAT   ! comentario no fim da linha
   10 CONTINUE
      END
"""
    for tok in tokenizar(codigo):
        print(tok)
