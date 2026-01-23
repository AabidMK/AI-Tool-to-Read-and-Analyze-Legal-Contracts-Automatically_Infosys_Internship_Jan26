from llm.classifier import classify_contract

def classification_node(file_path: str) -> dict:
    return classify_contract(file_path)
