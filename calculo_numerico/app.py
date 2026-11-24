from flask import Flask, jsonify, render_template, request

from resultado import ErroNumerico
from validador import para_float, para_funcao, para_inteiro, para_lista, para_matriz
from metodos import (Bisseccao, NewtonRaphson, Secante, FalsaPosicao,
                     EliminacaoGauss, FatoracaoLU, GaussSeidel,
                     Lagrange, NewtonInterpolador,
                     TrapezioRepetido, Simpson13Repetido, IntegracaoDiscreta)

app = Flask(__name__)

CAMPO_F = ("f", "f(x)", "x**3 - x - 2")
CAMPOS_AB = [("a", "a (início)", "1"), ("b", "b (fim)", "2")]
CAMPOS_TOL = [("tol", "Tolerância", "1e-6"), ("max_iter", "Máximo de iterações", "100")]
CAMPO_A = ("A", "Matriz A (uma linha por linha)", "2 1 -1\n-3 -1 2\n-2 1 2")
CAMPO_TERMOS = ("termos", "Vetor b (termos independentes)", "8 -11 -3")
CAMPOS_PONTOS = [("xs", "Valores de x", "0 1 2 3"), ("ys", "Valores de y", "1 2 5 10"),
                 ("x", "x a interpolar", "1.5")]
CAMPOS_INTEGRAL = [("f", "f(x)", "x**2"), ("a", "a (limite inferior)", "0"), ("b", "b (limite superior)", "3")]

METODOS = {
    "bisseccao": ("Raízes", "Bissecção", Bisseccao, [CAMPO_F] + CAMPOS_AB + CAMPOS_TOL),
    "newton": ("Raízes", "Newton-Raphson", NewtonRaphson, [CAMPO_F, ("x0", "x0 (aproximação inicial)", "1.5")] + CAMPOS_TOL),
    "secante": ("Raízes", "Secante", Secante, [CAMPO_F, ("x0", "x0", "1"), ("x1", "x1", "2")] + CAMPOS_TOL),
    "falsa": ("Raízes", "Falsa posição", FalsaPosicao, [CAMPO_F] + CAMPOS_AB + CAMPOS_TOL),

    "gauss": ("Sistemas lineares", "Eliminação de Gauss", EliminacaoGauss, [CAMPO_A, CAMPO_TERMOS]),
    "lu": ("Sistemas lineares", "Fatoração LU", FatoracaoLU, [CAMPO_A, CAMPO_TERMOS]),
    "seidel": ("Sistemas lineares", "Gauss-Seidel", GaussSeidel,
               [("A", CAMPO_A[1], "10 -1 2\n-1 11 -1\n2 -1 10"),
                ("termos", CAMPO_TERMOS[1], "6 25 -11"),
                ("chute", "Chute inicial", "0 0 0")] + CAMPOS_TOL),

    "lagrange": ("Interpolação", "Forma de Lagrange", Lagrange, CAMPOS_PONTOS),
    "newton_interp": ("Interpolação", "Forma de Newton", NewtonInterpolador, CAMPOS_PONTOS),

    "trapezio": ("Integração", "Trapézio repetido", TrapezioRepetido, CAMPOS_INTEGRAL + [("n", "Subintervalos n", "6")]),
    "simpson": ("Integração", "Simpson 1/3 repetido", Simpson13Repetido, CAMPOS_INTEGRAL + [("n", "Subintervalos n (par)", "6")]),
    "discreto": ("Integração", "Caso discreto", IntegracaoDiscreta,
                 [("xs", "Valores de x (crescentes)", "0 1 2 3 4"), ("ys", "Valores de f(x)", "0 1 4 9 16")]),
}

CAMPOS_LISTA = ["termos", "chute", "xs", "ys"]
CAMPOS_INTEIROS = ["max_iter", "n"]


def ler_campos(formulario, campos):
    dados = {}
    for campo in campos:
        nome = campo[0]
        texto = formulario.get(nome, "")

        if nome == "f":
            expressao, funcao = para_funcao(texto)
            dados["expr"] = expressao
            dados["f"] = funcao
        elif nome == "A":
            dados["A"] = para_matriz(texto)
        elif nome in CAMPOS_LISTA:
            dados[nome] = para_lista(texto, nome)
        elif nome in CAMPOS_INTEIROS:
            dados[nome] = para_inteiro(texto, nome)
        else:
            dados[nome] = para_float(texto, nome)

    if "tol" in dados and dados["tol"] <= 0:
        raise ErroNumerico("A tolerância deve ser maior que zero.")
    if "A" in dados:
        n = len(dados["A"])
        if len(dados["termos"]) != n:
            raise ErroNumerico("O vetor b deve ter " + str(n) + " valores (o mesmo tamanho da matriz A).")
        if "chute" in dados and len(dados["chute"]) != n:
            raise ErroNumerico("O chute inicial deve ter " + str(n) + " valores.")
    return dados


@app.get("/")
def pagina_inicial():
    grupos = {}
    for chave in METODOS:
        grupo, titulo, classe, campos = METODOS[chave]
        if grupo not in grupos:
            grupos[grupo] = []
        grupos[grupo].append((chave, titulo, campos))
    return render_template("index.html", grupos=grupos)


@app.post("/api/<chave>")
def calcular(chave):
    if chave not in METODOS:
        return jsonify(erro="Método desconhecido."), 404

    grupo, titulo, classe, campos = METODOS[chave]
    try:
        dados = ler_campos(request.get_json(force=True), campos)
        metodo = classe()
        resultado = metodo.executar(dados)
        return jsonify(resultado.to_dict())
    except ErroNumerico as erro:
        return jsonify(erro=str(erro)), 400


if __name__ == "__main__":
    app.run(debug=True)
