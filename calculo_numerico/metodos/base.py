from abc import ABC, abstractmethod


class MetodoNumerico(ABC):
    """Todo método recebe um dicionário de dados e devolve um Resultado."""

    @abstractmethod
    def executar(self, dados):
        pass
