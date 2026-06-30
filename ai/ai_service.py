from ai.ports.ai_port import AIPort, AI_FALLBACK_MESSAGE


class AIService:
    def __init__(self, port: AIPort) -> None:
        self._port: AIPort = port
        self._history: list[dict] = []

    def send(self, user_message: str) -> str:
        """Envia uma mensagem, atualiza o histórico e retorna a resposta."""
        response: str = self._port.ask(user_message, self._history)
        if response != AI_FALLBACK_MESSAGE:
            self._history.append({"role": "user", "content": user_message})
            self._history.append({"role": "assistant", "content": response})
        return response

    def clear_history(self) -> None:
        """Limpa o histórico da conversa."""
        self._history = []
