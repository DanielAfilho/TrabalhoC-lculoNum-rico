import math
from resultado import Resultado, ErroNumerico
from .base import MetodoNumerico

EPSILON = 1e-12


def matriz_para_texto(matriz):
    linhas = []
    for linha in matriz:
        partes = []
        for valor in linha:
            partes.append(f"{valor:9.4f}")
        linhas.append("  ".join(partes))
    return "\n".join(linhas)


class EliminacaoGauss(MetodoNumerico):
    def executar(self, d):
        A = d["A"]
        b = d["termos"]
        n = len(A)
        iteracoes = []

        M = []
        for i in range(n):
            linha = []
            for j in range(n):
                linha.append(A[i][j])
            linha.append(b[i])
            M.append(linha)

        for k in range(n):
            linha_pivo = k
            for i in range(k + 1, n):
                if abs(M[i][k]) > abs(M[linha_pivo][k]):
                    linha_pivo = i
            if abs(M[linha_pivo][k]) < EPSILON:
                raise ErroNumerico("A matriz é singular: o sistema não tem solução única.")

            if linha_pivo != k:
                M[k], M[linha_pivo] = M[linha_pivo], M[k]

            for i in range(k + 1, n):
                multiplicador = M[i][k] / M[k][k]
                for j in range(k, n + 1):
                    M[i][j] = M[i][j] - multiplicador * M[k][j]

            iteracoes.append({"etapa": k + 1, "matriz aumentada": matriz_para_texto(M)})

        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            soma = 0.0
            for j in range(i + 1, n):
                soma = soma + M[i][j] * x[j]
            x[i] = (M[i][n] - soma) / M[i][i]

        return Resultado(x, "x", iteracoes, "Solução por eliminação de Gauss.")


class FatoracaoLU(MetodoNumerico):
    def executar(self, d):
        A = d["A"]
        b = d["termos"]
        n = len(A)

        L = []
        U = []
        for i in range(n):
            linha_L = []
            linha_U = []
            for j in range(n):
                if i == j:
                    linha_L.append(1.0)
                else:
                    linha_L.append(0.0)
                linha_U.append(A[i][j])
            L.append(linha_L)
            U.append(linha_U)

        for k in range(n):
            if abs(U[k][k]) < EPSILON:
                raise ErroNumerico("Pivô nulo: reordene as equações para poder fatorar.")
            for i in range(k + 1, n):
                L[i][k] = U[i][k] / U[k][k]
                for j in range(k, n):
                    U[i][j] = U[i][j] - L[i][k] * U[k][j]

        iteracoes = []

        y = [0.0] * n
        for i in range(n):
            soma = 0.0
            for j in range(i):
                soma = soma + L[i][j] * y[j]
            y[i] = b[i] - soma
            iteracoes.append({"fase": "L y = b", "i": i + 1, "valor": y[i]})

        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            soma = 0.0
            for j in range(i + 1, n):
                soma = soma + U[i][j] * x[j]
            x[i] = (y[i] - soma) / U[i][i]
            iteracoes.append({"fase": "U x = y", "i": i + 1, "valor": x[i]})

        extra = {"Matriz L": matriz_para_texto(L), "Matriz U": matriz_para_texto(U)}
        return Resultado(x, "x", iteracoes, "Fatoração LU e substituições.", True, extra)


class GaussSeidel(MetodoNumerico):
    def executar(self, d):
        A = d["A"]
        b = d["termos"]
        tol = d["tol"]
        n = len(A)

        for i in range(n):
            if A[i][i] == 0:
                raise ErroNumerico("Há zero na diagonal principal: reordene as equações.")

        x = []
        for valor in d["chute"]:
            x.append(valor)

        iteracoes = []
        for k in range(1, d["max_iter"] + 1):
            maior_erro = 0.0
            for i in range(n):
                soma = 0.0
                for j in range(n):
                    if j != i:
                        soma = soma + A[i][j] * x[j]
                x_novo = (b[i] - soma) / A[i][i]

                diferenca = abs(x_novo - x[i])
                if diferenca > maior_erro:
                    maior_erro = diferenca
                x[i] = x_novo

            if not math.isfinite(maior_erro):
                raise ErroNumerico("O método divergiu. Tente reordenar as equações.")

            linha = {"k": k}
            for i in range(n):
                linha["x" + str(i + 1)] = x[i]
            linha["erro"] = maior_erro
            iteracoes.append(linha)

            if maior_erro < tol:
                return Resultado(x, "x", iteracoes, "Convergiu em " + str(k) + " iterações.")

        return Resultado(x, "x", iteracoes, "Não convergiu no máximo de iterações.", False)
