from retrieval_node import retrieve_clauses
from analyze_contract import analyze_contract

contract_text = """
This Shareholder Agreement allows shareholders to transfer shares
with approval and defines voting rights.
"""

contract_type = "Shareholder Agreement"

# Retrieve similar clauses
retrieved_clauses = retrieve_clauses(
    query="share transfer and voting rights",
    contract_type=contract_type
)

# Analyze contract
analysis = analyze_contract(  
    contract_text=contract_text,
    retrieved_clauses=retrieved_clauses,
    contract_type=contract_type
)

print("\n===== ANALYZE CONTRACT OUTPUT =====\n")
print(analysis)


