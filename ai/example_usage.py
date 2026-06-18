"""
Exemplo standalone para testar a integração com OpenAI sem abrir o jogo.
Uso: uv run ai/example_usage.py
"""

from ai import build_ai_service

ai = build_ai_service()

print("=== Fantasy Valley — AI Test ===")
print("Digite 'sair' para encerrar, 'limpar' para resetar o histórico.\n")

while True:
    user_input: str = input("Você: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "sair":
        break
    if user_input.lower() == "limpar":
        ai.clear_history()
        print("[histórico limpo]\n")
        continue

    response: str = ai.send(user_input)
    print(f"IA: {response}\n")
