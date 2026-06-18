import os

from dotenv import load_dotenv
from openai import OpenAI

from ai.ports.ai_port import AIPort

load_dotenv(override=True)


class OpenAIAdapter(AIPort):
    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
    ) -> None:
        self._client: OpenAI = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model: str = model or os.getenv("AI_MODEL", "gpt-4o")
        self._temperature: float = temperature if temperature is not None else float(os.getenv("AI_TEMPERATURE", "0.7"))

    def ask(self, message: str, history: list[dict]) -> str:
        messages: list[dict] = [*history, {"role": "user", "content": message}]
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
        )
        return response.choices[0].message.content or ""
