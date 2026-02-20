from langchain_ollama import ChatOllama

def get_llm():
    return ChatOllama(
        model="qwen2.5:14b-instruct-q5_K_M",
        temperature=0.0
    )
