import sympy as sp
from validador import X, compilar
from resultado import Resultado, ErroNumerico
from .base import MetodoNumerico


def verificar_intervalo(d):
    a = d["a"]
    b = d["b"]
    f = d["f"]
    if a >= b:
        raise ErroNumerico("Intervalo inválido: é preciso ter a < b.")
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        raise ErroNumerico("f(a) e f(b) têm o mesmo sinal: não há garantia de raiz no intervalo.")
    return a, b, fa, fb


def montar_resultado(raiz, iteracoes, convergiu):
    if convergiu:
        mensagem = "Convergiu em " + str(len(iteracoes)) + " iterações."
    else:
        mensagem = "Não convergiu no máximo de iterações."
    return Resultado(raiz, "raiz", iteracoes, mensagem, convergiu)


class Bisseccao(MetodoNumerico):
    def executar(self, d):
        f = d["f"]
        tol = d["tol"]
        a, b, fa, fb = verificar_intervalo(d)
        iteracoes = []

        for k in range(1, d["max_iter"] + 1):
            xm = (a + b) / 2          # ponto médio
            fxm = f(xm)
            erro = (b - a) / 2
            iteracoes.append({"k": k, "a": a, "b": b, "xm": xm, "f(xm)": fxm, "erro": erro})

            if abs(fxm) < tol or erro < tol:
                return montar_resultado(xm, iteracoes, True)

            if fa * fxm < 0:
                b = xm
            else:
                a = xm
                fa = fxm

        return montar_resultado(xm, iteracoes, False)


class FalsaPosicao(MetodoNumerico):
    def executar(self, d):
        f = d["f"]
        tol = d["tol"]
        a, b, fa, fb = verificar_intervalo(d)
        iteracoes = []
        x_anterior = a

        for k in range(1, d["max_iter"] + 1):
            x = (a * fb - b * fa) / (fb - fa)
            fx = f(x)
            erro = abs(x - x_anterior)
            iteracoes.append({"k": k, "a": a, "b": b, "x": x, "f(x)": fx, "erro": erro})

            if abs(fx) < tol:
                return montar_resultado(x, iteracoes, True)
            if k > 1 and erro < tol:
                return montar_resultado(x, iteracoes, True)

            if fa * fx < 0:
                b = x
                fb = fx
            else:
                a = x
                fa = fx
            x_anterior = x

        return montar_resultado(x, iteracoes, False)


class NewtonRaphson(MetodoNumerico):
    def executar(self, d):
        f = d["f"]
        tol = d["tol"]
        x = d["x0"]

        derivada = sp.diff(d["expr"], X)
        df = compilar(derivada)

        iteracoes = []
        for k in range(1, d["max_iter"] + 1):
            fx = f(x)
            dfx = df(x)
            if abs(dfx) < 1e-14:
                raise ErroNumerico("A derivada é quase zero em x = " + str(x) + ". Escolha outro x0.")

            x_novo = x - fx / dfx
            erro = abs(x_novo - x)
            iteracoes.append({"k": k, "x": x, "f(x)": fx, "f'(x)": dfx, "x seguinte": x_novo, "erro": erro})
            x = x_novo

            if erro < tol or abs(f(x)) < tol:
                resultado = montar_resultado(x, iteracoes, True)
                resultado.extra = {"Derivada calculada pelo sympy": str(derivada)}
                return resultado

        return montar_resultado(x, iteracoes, False)


class Secante(MetodoNumerico):
    def executar(self, d):
        f = d["f"]
        tol = d["tol"]
        x0 = d["x0"]
        x1 = d["x1"]
        if x0 == x1:
            raise ErroNumerico("x0 e x1 devem ser diferentes.")
        iteracoes = []

        for k in range(1, d["max_iter"] + 1):
            f0 = f(x0)
            f1 = f(x1)
            if f0 == f1:
                raise ErroNumerico("f(x0) = f(x1): divisão por zero.")

            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            erro = abs(x2 - x1)
            iteracoes.append({"k": k, "x_k-1": x0, "x_k": x1, "x_k+1": x2, "erro": erro})

            x0 = x1
            x1 = x2
            if erro < tol or abs(f(x1)) < tol:
                return montar_resultado(x1, iteracoes, True)

        return montar_resultado(x1, iteracoes, False)
