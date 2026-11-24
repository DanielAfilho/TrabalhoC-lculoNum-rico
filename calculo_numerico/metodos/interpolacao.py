import sympy as sp
from validador import X
from resultado import Resultado, ErroNumerico
from .base import MetodoNumerico


def verificar_pontos(xs, ys):
    if len(xs) != len(ys):
        raise ErroNumerico("Os campos x e y devem ter a mesma quantidade de valores.")
    if len(xs) < 2:
        raise ErroNumerico("Informe pelo menos 2 pontos.")
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] == xs[j]:
                raise ErroNumerico("Os valores de x não podem se repetir.")


def polinomio_com_sympy(xs, ys):
    pontos = []
    for i in range(len(xs)):
        pontos.append((sp.Rational(str(xs[i])), sp.Rational(str(ys[i]))))
    polinomio = sp.interpolate(pontos, X)
    return {"Polinômio P(x) (sympy)": str(sp.expand(polinomio))}


class Lagrange(MetodoNumerico):
    def executar(self, d):
        xs = d["xs"]
        ys = d["ys"]
        x = d["x"]
        verificar_pontos(xs, ys)
        n = len(xs)

        resultado = 0.0
        iteracoes = []
        for i in range(n):
            Li = 1.0
            for j in range(n):
                if j != i:
                    Li = Li * (x - xs[j]) / (xs[i] - xs[j])
            parcela = ys[i] * Li
            resultado = resultado + parcela
            iteracoes.append({"i": i, "x_i": xs[i], "y_i": ys[i], "L_i(x)": Li, "y_i * L_i(x)": parcela})

        return Resultado(resultado, "P(x)", iteracoes, "Interpolação de Lagrange.", True,
                         polinomio_com_sympy(xs, ys))


class NewtonInterpolador(MetodoNumerico):
    def executar(self, d):
        xs = d["xs"]
        ys = d["ys"]
        x = d["x"]
        verificar_pontos(xs, ys)
        n = len(xs)

        tabela = [ys]
        for ordem in range(1, n):
            coluna = []
            for i in range(n - ordem):
                anterior = tabela[ordem - 1]
                numerador = anterior[i + 1] - anterior[i]
                denominador = xs[i + ordem] - xs[i]
                coluna.append(numerador / denominador)
            tabela.append(coluna)

        resultado = tabela[0][0]
        produto = 1.0
        for i in range(1, n):
            produto = produto * (x - xs[i - 1])
            resultado = resultado + tabela[i][0] * produto

        iteracoes = []
        for i in range(n):
            linha = {"i": i, "x_i": xs[i]}
            for ordem in range(n - i):
                linha["ordem " + str(ordem)] = tabela[ordem][i]
            iteracoes.append(linha)

        return Resultado(resultado, "P(x)", iteracoes, "Diferenças divididas de Newton.", True,
                         polinomio_com_sympy(xs, ys))
