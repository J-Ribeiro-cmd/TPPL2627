# Testes do lexer. Correr a partir da raiz do repositorio:
#   python3 tests/test_lexer.py
import os
import sys
import glob

PASTA_TESTES = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PASTA_TESTES, '..', 'src'))

from lexer import tokenizar, lexer


# ---------- funcoes auxiliares ----------

def tipos(codigo):
    "Lista so com os tipos dos tokens, ex: ['ID', '=', 'INT', 'NEWLINE']"
    return [t.type for t in tokenizar(codigo)]

def tipos_e_valores(codigo):
    "Lista de pares (tipo, valor), ex: [('ID', 'X'), ('=', '='), ('INT', 1)]"
    return [(t.type, t.value) for t in tokenizar(codigo)]

def ler(caminho):
    with open(caminho) as f:
        return f.read()


# ---------- exemplos do enunciado ----------

def test_exemplos_sem_erros():
    for ficheiro in sorted(glob.glob(os.path.join(PASTA_TESTES, 'exemplos', '*.f'))):
        tokenizar(ler(ficheiro))
        assert lexer.erros == [], f"{os.path.basename(ficheiro)}: {lexer.erros}"

def test_exemplos_newlines_limpos():
    # um so NEWLINE por instrucao: nenhum no inicio, nenhum repetido, um no fim
    for ficheiro in sorted(glob.glob(os.path.join(PASTA_TESTES, 'exemplos', '*.f'))):
        t = tipos(ler(ficheiro))
        nome = os.path.basename(ficheiro)
        assert t[0] != 'NEWLINE', f"{nome}: NEWLINE no inicio"
        assert t[-1] == 'NEWLINE', f"{nome}: falta o NEWLINE no fim"
        for a, b in zip(t, t[1:]):
            assert not (a == 'NEWLINE' and b == 'NEWLINE'), f"{nome}: NEWLINE repetido"

def test_fatorial_ciclo_do():
    t = tipos_e_valores(ler(os.path.join(PASTA_TESTES, 'exemplos', 'ex2_fatorial.f')))
    # linha 'DO 10 I = 1, N' (o 10 e um INT, nao um LABEL)
    assert ('DO', 'DO') in t
    i = t.index(('DO', 'DO'))
    assert t[i:i+8] == [('DO', 'DO'), ('INT', 10), ('ID', 'I'), ('=', '='),
                        ('INT', 1), (',', ','), ('ID', 'N'), ('NEWLINE', '\n')]
    # linha '10 CONTINUE' (aqui o 10 e um LABEL)
    assert ('LABEL', 10) in t


# ---------- requisitos do enunciado, um a um ----------

def test_maiusculas_minusculas():
    assert tipos_e_valores("program teste") == [('PROGRAM', 'PROGRAM'), ('ID', 'TESTE'), ('NEWLINE', '\n')]
    assert tipos("x = .true. .And. y .le. 3") == ['ID', '=', 'TRUE', 'AND', 'ID', 'LE', 'INT', 'NEWLINE']

def test_strings_mantem_texto():
    assert tipos_e_valores("PRINT *, 'Ola, Mundo!'")[3] == ('STRING', 'Ola, Mundo!')
    assert tipos_e_valores("PRINT *, 'It''s'")[3] == ('STRING', "It's")

def test_numeros():
    assert tipos_e_valores("X = 3.14 + 3. + .5 + 1.0E-3 + 2E5")[2::2] == [
        ('REALNUM', 3.14), ('REALNUM', 3.0), ('REALNUM', 0.5), ('REALNUM', 0.001), ('REALNUM', 200000.0)]

def test_operadores():
    assert tipos("A .EQ. B .NE. C .LT. D .LE. E .GT. F .GE. G") == [
        'ID', 'EQ', 'ID', 'NE', 'ID', 'LT', 'ID', 'LE', 'ID', 'GT', 'ID', 'GE', 'ID', 'NEWLINE']
    assert tipos(".NOT. A .AND. B .OR. C") == ['NOT', 'ID', 'AND', 'ID', 'OR', 'ID', 'NEWLINE']
    assert tipos("X = 2 ** 3 + 1 - 2 * 3 / 4") == ['ID', '=', 'INT', 'POW', 'INT', '+', 'INT', '-',
                                                   'INT', '*', 'INT', '/', 'INT', 'NEWLINE']

def test_ponto_numero_vs_operador():
    # 1.EQ.N nao pode ser lido como o real 1. seguido de lixo
    # (dentro de um IF, porque um numero no inicio da linha seria um LABEL)
    assert tipos_e_valores("IF (1.EQ.N)")[2:5] == [('INT', 1), ('EQ', '.EQ.'), ('ID', 'N')]

def test_labels():
    assert tipos_e_valores("   10 CONTINUE")[0] == ('LABEL', 10)
    assert tipos_e_valores("GOTO 10")[1] == ('INT', 10)

def test_comentarios():
    codigo = "C comentario\n* outro\nX = 1 ! fim de linha\nc minusculo\nY = 2"
    assert tipos(codigo) == ['ID', '=', 'INT', 'NEWLINE', 'ID', '=', 'INT', 'NEWLINE']
    assert lexer.erros == []

def test_variavel_chamada_c():
    assert tipos("C = 2\nC(1) = 3") == ['ID', '=', 'INT', 'NEWLINE', 'ID', '(', 'INT', ')', '=', 'INT', 'NEWLINE']

def test_linhas_em_branco():
    # linhas vazias ou so com espacos nao geram NEWLINE extra
    assert tipos("\n\nPROGRAM X\n   \n\n  \nEND\n\n") == ['PROGRAM', 'ID', 'NEWLINE', 'END', 'NEWLINE']

def test_formas_com_espaco():
    assert tipos("ELSEIF") == ['ELSEIF', 'NEWLINE']
    assert tipos_e_valores("GO TO 10")[:2] == [('GO', 'GO'), ('ID', 'TO')]


# ---------- erros ----------

def test_erro_caracter():
    tokenizar(ler(os.path.join(PASTA_TESTES, 'erros', 'erro_caracter.f')))
    assert lexer.erros == ["Erro lexico na linha 3: caracter ilegal '@'"]

def test_erro_string():
    tokenizar(ler(os.path.join(PASTA_TESTES, 'erros', 'erro_string.f')))
    assert len(lexer.erros) == 1 and lexer.erros[0].startswith("Erro lexico na linha 2: string nao fechada")

def test_varios_erros():
    # o lexer nao para no primeiro erro: apanha todos
    tokenizar(ler(os.path.join(PASTA_TESTES, 'erros', 'erro_varios.f')))
    assert len(lexer.erros) == 2
    assert "linha 3" in lexer.erros[0] and "linha 4" in lexer.erros[1]

def test_erros_limpos_entre_programas():
    tokenizar("X = 1 @ 2")
    tokenizar("X = 1")
    assert lexer.erros == []


# ---------- correr todos os testes ----------

if __name__ == '__main__':
    import io, contextlib
    testes = [(nome, f) for nome, f in list(globals().items()) if nome.startswith('test_')]
    falhas = 0
    for nome, f in testes:
        try:
            with contextlib.redirect_stdout(io.StringIO()):   # esconde os prints dos erros lexicos
                f()
            print(f"OK      {nome}")
        except AssertionError as e:
            falhas += 1
            print(f"FALHOU  {nome}: {e}")
    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram")
    sys.exit(1 if falhas else 0)
