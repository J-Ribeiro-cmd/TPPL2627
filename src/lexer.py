import ply.lex as lex

reserved = {
    'PROGRAM' : 'PROGRAM',
    'END' : 'END',
    'STOP' : 'STOP',
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
    'SUBROUTINE' : 'SUBROUTINE',
    'CALL' : 'CALL',
    'RETURN' : 'RETURN',
}

tokens = ['ID', 'NEWLINE',
    'INT', 'LABEL', 'REALNUM', 'STRING',
    'TRUE', 'FALSE', 'EQ', 'NE',
    'LT', 'LE', 'GT', 'GE', 'AND',
    'OR', 'NOT', 'POW'
] + list(reserved.values())

literals = "+-*/=(),"

# Estado para as linhas de comentario (C, c ou * no inicio da linha)
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

t_ignore_COMMENT = r'![^\n]*'      # ! em qualquer posicao, ate ao fim da linha

# Tem de ser a PRIMEIRA funcao (o ply testa as funcoes pela ordem do ficheiro).
# Comentario: linha cujo primeiro caracter nao branco e '*', ou C/c seguido de espaco.
# Excecao: 'C = ...' e 'C(...)' sao instrucoes (variavel ou array chamado C).
def t_INICIO_COMENTARIO(t):
    r'\n+[ \t]*(\*|[Cc](?![ \t]*[=(])(?=[ \t\n]))'
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('comentario')

def t_comentario_FIM(t):
    r'(?=\n)'                      # nao consome o \n: a linha seguinte pode ser outro comentario
    t.lexer.begin('INITIAL')

def t_comentario_TEXTO(t):
    r'[^\n]+'
    pass

t_comentario_ignore = ''

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# Tem de vir antes do t_INT. Aceita 3.14, 3., .5, 1.0E-3 e 2E5,
# mas nao parte o 1.EQ.2 (o ponto nao pode ser seguido de letras e outro ponto).
def t_REALNUM(t):
    r'(\d+\.(?![A-Za-z]+\.)\d*|\.\d+)([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+'
    t.value = float(t.value)
    return t

# Um inteiro que e a primeira coisa da linha e um LABEL (ex: 10 CONTINUE).
def t_INT(t):
    r'\d+'
    inicio_linha = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
    if t.lexer.lexdata[inicio_linha:t.lexpos].strip() == '':
        t.type = 'LABEL'
    t.value = int(t.value)
    return t

# '' dentro da string representa uma aspa: 'It''s' -> It's
def t_STRING(t):
    r"'([^'\n]|'')*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t

# So encaixa se o t_STRING falhar: aspa sem a aspa final na mesma linha
def t_STRING_ABERTA(t):
    r"'[^\n]*"
    print(f"Erro lexico na linha {t.lexer.lineno}: string nao fechada {t.value}")

t_ignore = ' \t'

# t_ANY_error em vez de t_error, para valer tambem no estado 'comentario'
def t_ANY_error(t):
    print(f"Erro lexico na linha {t.lexer.lineno}: caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Usar sempre esta funcao em vez de lexer.input(codigo)
def tokenizar(codigo):
    if not codigo.endswith('\n'):  # garante que a ultima linha termina em \n
        codigo += '\n'
    lexer.lineno = 0               # compensa o \n extra do inicio
    lexer.begin('INITIAL')
    lexer.input('\n' + codigo)     # o \n inicial deixa a 1a linha ser comentario
    return list(lexer)


# Teste: só corre quando executamos este ficheiro diretamente
if __name__ == '__main__':
    codigo = """C comentario na primeira linha
* comentario com asterisco
X = 3.14 + 3. + 1.0E-3 + 2E5
IF (N.EQ.2 .AND. 1.EQ.N) GOTO 10
PRINT *, 'It''s', 'abc
   10 CONTINUE
DO 20 I = 1, N
Y = 1 @ 2
C = 2
STOP
END"""
    for tok in tokenizar(codigo):
        print(tok)
