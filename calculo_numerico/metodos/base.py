from abc import ABC, abstractmethod


class MetodoNumerico(ABC):

    @abstractmethod
    def executar(self, dados):
        pass
