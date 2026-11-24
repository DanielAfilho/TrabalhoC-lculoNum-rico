from resultado import Resultado, ErroNumerico
from .base import MetodoNumerico

MAX_LINHAS_TABELA = 200


def gerar_pontos(d):
    f = d["f"]
    a = d["a"]
    b = d["b"]
    n = d["n"]
    if a >= b:
        raise ErroNumerico("O limite inferior deve ser menor que o superior.")

    h = (b - a) / n
    xs = []
    fs = []
    for i in range(n + 1):
        x = a + i * h
        xs.append(x)
        fs.append(f(x))
    return xs, fs, h


def montar_tabela(xs, fs):
    tabela = []
    for i in range(len(xs)):
        if i >= MAX_LINHAS_TABELA:
            break
        tabela.append({"i": i, "x_i": xs[i], "f(x_i)": fs[i]})
    return tabela


class TrapezioRepetido(MetodoNumerico):
    def executar(self, d):
        n = d["n"]
        xs, fs, h = gerar_pontos(d)

        soma = fs[0] + fs[n]
        for i in range(1, n):
            soma = soma + 2 * fs[i]
        integral = h / 2 * soma

        mensagem = "Trapézio repetido com n = " + str(n) + " e h = " + str(h) + "."
        return Resultado(integral, "integral", montar_tabela(xs, fs), mensagem)


class Simpson13Repetido(MetodoNumerico):
    def executar(self, d):
        n = d["n"]
        if n % 2 != 0:
            raise ErroNumerico("Em Simpson 1/3 o número de subintervalos n deve ser par.")
        xs, fs, h = gerar_pontos(d)
        soma = fs[0] + fs[n]
        for i in range(1, n):
            if i % 2 == 1:
                soma = soma + 4 * fs[i]
            else:
                soma = soma + 2 * fs[i]
        integral = h / 3 * soma

        mensagem = "Simpson 1/3 repetido com n = " + str(n) + " e h = " + str(h) + "."
        return Resultado(integral, "integral", montar_tabela(xs, fs), mensagem)


class IntegracaoDiscreta(MetodoNumerico):

    def executar(self, d):
        xs = d["xs"]
        ys = d["ys"]

        if len(xs) != len(ys):
            raise ErroNumerico("x e f(x) devem ter a mesma quantidade de valores.")
        if len(xs) < 2:
            raise ErroNumerico("Informe pelo menos 2 pontos.")
        for i in range(len(xs) - 1):
            if xs[i + 1] <= xs[i]:
                raise ErroNumerico("Os valores de x devem estar em ordem crescente e sem repetição.")

        n = len(xs) - 1
        h = xs[1] - xs[0]

        espacamento_igual = True
        for i in range(n):
            if abs((xs[i + 1] - xs[i]) - h) > 1e-9:
                espacamento_igual = False

        if espacamento_igual and n % 2 == 0:
            soma = ys[0] + ys[n]
            for i in range(1, n):
                if i % 2 == 1:
                    soma = soma + 4 * ys[i]
                else:
                    soma = soma + 2 * ys[i]
            integral = h / 3 * soma
            regra = "Simpson 1/3"
        else:
            integral = 0.0
            for i in range(n):
                largura = xs[i + 1] - xs[i]
                integral = integral + largura * (ys[i] + ys[i + 1]) / 2
            regra = "Trapézio"

        return Resultado(integral, "integral", montar_tabela(xs, ys), "Regra usada: " + regra + ".")
