from parser.document_parser import ContractDocumentParser
from classification.graph import build_classification_graph
from retrieval.graph import build_retrieval_graph
from analysis.graph import build_analysis_graph

# 1. Parse document
parser = ContractDocumentParser()
markdown_text = parser.parse_and_return_text("EX-10.1.pdf")

# 2. Classification
classification_graph = build_classification_graph()
classification_result = classification_graph.invoke({
    "markdown_text": markdown_text
})

contract_type = classification_result["classification"]["contract_type"]

# 3. Retrieval
retrieval_graph = build_retrieval_graph()
retrieval_result = retrieval_graph.invoke({
    "query": "employment obligations confidentiality termination",
    "contract_type": contract_type
})

retrieved_clauses = retrieval_result["retrieved_clauses"]

# 4. Analyze (NEW)
analysis_graph = build_analysis_graph()
analysis_result = analysis_graph.invoke({
    "markdown_text": markdown_text,
    "contract_type": contract_type,
    "retrieved_clauses": retrieved_clauses
})

print("===== ANALYSIS RESULT =====")
print(analysis_result)