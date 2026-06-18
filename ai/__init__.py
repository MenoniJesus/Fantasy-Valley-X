from ai.adapters.openai_adapter import OpenAIAdapter
from ai.ai_service import AIService


def build_ai_service() -> AIService:
    return AIService(port=OpenAIAdapter())
