from app import app, METODOS

cliente = app.test_client()


def rodar(chave, **alterar):
    campos = {}
    for nome, rotulo, exemplo in METODOS[chave][3]:
        campos[nome] = exemplo
    for nome in alterar:
        campos[nome] = str(alterar[nome])
    resposta = cliente.post("/api/" + chave, json=campos)
    return resposta.status_code, resposta.get_json()


def conferir(descricao, condicao):
    if condicao:
        print("OK    " + descricao)
    else:
        print("FALHOU " + descricao)
        raise AssertionError(descricao)


for chave in ["bisseccao", "falsa", "newton", "secante"]:
    status, json = rodar(chave)
    conferir(chave + ": raiz de x^3 - x - 2", abs(json["valor"] - 1.5213797068) < 1e-5)


for chave in ["gauss", "lu"]:
    status, json = rodar(chave)
    esperado = [2, 3, -1]
    certo = True
    for i in range(3):
        if abs(json["valor"][i] - esperado[i]) > 1e-9:
            certo = False
    conferir(chave + ": x = (2, 3, -1)", certo)


status, json = rodar("seidel")
conferir("seidel: convergiu", json["sucesso"] is True)


for chave in ["lagrange", "newton_interp"]:
    status, json = rodar(chave)
    conferir(chave + ": P(1.5) = 3.25", abs(json["valor"] - 3.25) < 1e-12)
    conferir(chave + ": polinômio x**2 + 1", json["extra"]["Polinômio P(x) (sympy)"] == "x**2 + 1")


status, json = rodar("trapezio", n=1000)
conferir("trapézio ≈ 9", abs(json["valor"] - 9) < 1e-4)
status, json = rodar("simpson")
conferir("simpson = 9", abs(json["valor"] - 9) < 1e-12)
status, json = rodar("discreto")
conferir("discreto = 64/3", abs(json["valor"] - 64 / 3) < 1e-12)
status, json = rodar("simpson", f="sin(x)", a=0, b="pi", n=100)
conferir("simpson: integral de sen(x) em [0, pi] ≈ 2", abs(json["valor"] - 2) < 1e-6)


print("--- entradas inválidas")
casos = [
    ("bisseccao", {"a": 3, "b": 4}),
    ("bisseccao", {"f": "x**y"}),
    ("bisseccao", {"tol": "abc"}),
    ("bisseccao", {"f": "1/x", "a": -1, "b": 1}),
    ("newton", {"f": "x**2+1", "x0": 0}),
    ("simpson", {"n": 5}),
    ("gauss", {"A": "1 2\n2 4", "termos": "1 2"}),
    ("gauss", {"A": "1 2 3\n4 5 6"}),
    ("gauss", {"termos": "1 2"}),
    ("lagrange", {"xs": "1 1 2", "ys": "1 2 3"}),
    ("discreto", {"xs": "3 2 1", "ys": "1 2 3"}),
]
for chave, alteracoes in casos:
    status, json = rodar(chave, **alteracoes)
    print("  " + chave + " " + str(alteracoes) + " -> " + json["erro"])
    assert status == 400
