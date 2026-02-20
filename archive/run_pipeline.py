from parser.document_parser import ContractDocumentParser
from classification.graph import build_classification_graph
from retrieval.graph import build_retrieval_graph

# 1. Parse document
parser = ContractDocumentParser()
text = parser.parse_and_return_text("EX-10.1.pdf")

# 2. Classification
classification_graph = build_classification_graph()
classification_result = classification_graph.invoke({
    "markdown_text": text
})

contract_type = classification_result["classification"]["contract_type"]

# 3. Retrieval
retrieval_graph = build_retrieval_graph()
retrieval_result = retrieval_graph.invoke({
    "query": "confidential information disclosure",
    "contract_type": contract_type
})

print(retrieval_result)