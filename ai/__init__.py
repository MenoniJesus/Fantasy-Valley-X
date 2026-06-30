from ai.adapters.openai_adapter import OpenAIAdapter
from ai.adapters.ollama_adapter import OllamaAdapter

from ai.ai_service import AIService


def build_ai_service() -> AIService:
    #return AIService(port=OllamaAdapter(
    #    host="http://localhost:11434", model="deepseek-r1:7b", max_tokens=600,
    #))

    return AIService(port=OpenAIAdapter())
