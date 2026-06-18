from abc import ABC, abstractmethod


class AIPort(ABC):
    """Contrato que todo provider de IA deve implementar."""

    @abstractmethod
    def ask(self, message: str, history: list[dict]) -> str:
        """Envia uma mensagem com histórico e retorna a resposta do modelo."""
