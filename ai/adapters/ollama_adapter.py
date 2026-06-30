import logging

import httpx

from ai.ports.ai_port import AIPort, AI_FALLBACK_MESSAGE

logger = logging.getLogger(__name__)

MAX_ATTEMPTS: int = 3 


class OllamaAdapter(AIPort):
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "deepseek-r1:7b",
        temperature: float = 0.5,
        max_tokens: int | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._host: str = host
        self._model: str = model
        self._temperature: float = temperature
        self._max_tokens: int | None = max_tokens
        self._timeout: float = timeout

    def ask(self, message: str, history: list[dict]) -> str:
        messages: list[dict] = [*history, {"role": "user", "content": message}]
        options: dict = {"temperature": self._temperature}
        if self._max_tokens is not None:
            options["num_predict"] = self._max_tokens

        payload: dict = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": options,
        }

        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = httpx.post(
                    f"{self._host}/api/chat",
                    json=payload,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"] or ""
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "Tentativa %d/%d de falar com o Ollama em %s falhou: %s",
                    attempt,
                    MAX_ATTEMPTS,
                    self._host,
                    exc,
                )

        logger.error(
            "Ollama indisponível em %s após %d tentativas: %s",
            self._host,
            MAX_ATTEMPTS,
            last_error,
        )
        return AI_FALLBACK_MESSAGE
