import logging
import os

from dotenv import load_dotenv
from openai import APIError, OpenAI

from ai.ports.ai_port import AIPort, AI_FALLBACK_MESSAGE

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class OpenAIAdapter(AIPort):
    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
    ) -> None:
        self._client: OpenAI = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model: str = model or os.getenv("AI_MODEL", "gpt-4.1-nano")
        self._temperature: float = temperature if temperature is not None else float(os.getenv("AI_TEMPERATURE", "0.7"))

    def ask(self, message: str, history: list[dict]) -> str:
        messages: list[dict] = [*history, {"role": "user", "content": message}]
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
            )
            return response.choices[0].message.content or ""
        except APIError as exc:
            logger.error("OpenAI indisponível (%s): %s", self._model, exc)
            return AI_FALLBACK_MESSAGE
