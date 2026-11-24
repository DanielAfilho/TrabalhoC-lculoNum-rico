class ErroNumerico(Exception):
    pass


class Resultado:

    def __init__(self, valor, rotulo, iteracoes, mensagem, sucesso=True, extra=None):
        self.valor = valor
        self.rotulo = rotulo
        self.iteracoes = iteracoes
        self.mensagem = mensagem
        self.sucesso = sucesso
        if extra is None:
            extra = {}
        self.extra = extra

    def to_dict(self):
        return {
            "valor": self.valor,
            "rotulo": self.rotulo,
            "iteracoes": self.iteracoes,
            "mensagem": self.mensagem,
            "sucesso": self.sucesso,
            "extra": self.extra,
        }
