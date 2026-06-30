from abc import ABC, abstractmethod

AI_FALLBACK_MESSAGE: str = "ZZZZZzzzzzzz"


class AIPort(ABC):
    @abstractmethod
    def ask(self, message: str, history: list[dict]) -> str:
        """Envia uma mensagem com histórico e retorna a resposta do modelo."""
