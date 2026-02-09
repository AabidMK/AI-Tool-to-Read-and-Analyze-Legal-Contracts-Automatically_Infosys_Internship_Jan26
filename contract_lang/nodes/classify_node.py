from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def classify_contract_node(state: dict):
    prompt = f"""
    Identify the contract type from the text below.
    Only return the contract type name.

    TEXT:
    {state['contract_text']}
    """

    contract_type = llm.invoke(prompt).strip()

    print(f"✅ Contract classified as: {contract_type}")
    return {"contract_type": contract_type}
