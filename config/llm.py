from langchain_ollama import ChatOllama

def get_llm(temperature: float = 0):
    return ChatOllama(
        model = "qwen2.5:14b-instruct-q5_K_M",
        temperature=temperature
    )