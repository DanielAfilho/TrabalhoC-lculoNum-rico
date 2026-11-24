import math
import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application, convert_xor)
from resultado import ErroNumerico

X = sp.Symbol("x")
TRANSFORMACOES = standard_transformations + (implicit_multiplication_application, convert_xor)


def interpretar(texto, nome_do_campo):
    texto = texto.strip()
    texto = texto.replace(",", ".")
    if texto == "":
        raise ErroNumerico("O campo '" + nome_do_campo + "' está vazio.")
    try:
        return parse_expr(texto, local_dict={"x": X, "e": sp.E}, transformations=TRANSFORMACOES)
    except Exception:
        raise ErroNumerico("Não foi possível interpretar '" + texto + "' no campo '" + nome_do_campo + "'.")


def para_float(texto, nome_do_campo):
    expressao = interpretar(texto, nome_do_campo)
    if len(expressao.free_symbols) > 0:
        raise ErroNumerico("O campo '" + nome_do_campo + "' deve ser um número (ex.: 0.5, 1e-6, pi/2).")
    valor = float(expressao)
    if not math.isfinite(valor):
        raise ErroNumerico("O campo '" + nome_do_campo + "' deve ser um número finito.")
    return valor


def para_inteiro(texto, nome_do_campo):
    valor = para_float(texto, nome_do_campo)
    if valor != int(valor):
        raise ErroNumerico("O campo '" + nome_do_campo + "' deve ser um número inteiro.")
    if valor < 1 or valor > 100000:
        raise ErroNumerico("O campo '" + nome_do_campo + "' deve estar entre 1 e 100000.")
    return int(valor)


def compilar(expressao):
    funcao_rapida = sp.lambdify(X, expressao, "math")

    def avaliar(x):
        try:
            valor = float(funcao_rapida(x))
        except (ZeroDivisionError, ValueError, OverflowError, TypeError):
            raise ErroNumerico("Não foi possível calcular f(" + str(x) + ").")
        if not math.isfinite(valor):
            raise ErroNumerico("f(" + str(x) + ") não é um número finito.")
        return valor

    return avaliar


def para_funcao(texto):
    expressao = interpretar(texto, "f(x)")
    for simbolo in expressao.free_symbols:
        if simbolo != X:
            raise ErroNumerico("A função deve usar apenas a variável x.")
    return expressao, compilar(expressao)


def para_lista(texto, nome_do_campo):
    pedacos = texto.split()
    if len(pedacos) == 0:
        raise ErroNumerico("O campo '" + nome_do_campo + "' está vazio.")
    lista = []
    for pedaco in pedacos:
        lista.append(para_float(pedaco, nome_do_campo))
    return lista


def para_matriz(texto):
    matriz = []
    for linha in texto.splitlines():
        if linha.strip() != "":
            matriz.append(para_lista(linha, "matriz A"))
    n = len(matriz)
    if n == 0:
        raise ErroNumerico("A matriz A está vazia.")
    for linha in matriz:
        if len(linha) != n:
            raise ErroNumerico("A matriz A deve ser quadrada (mesmo número de linhas e colunas).")
    return matriz
