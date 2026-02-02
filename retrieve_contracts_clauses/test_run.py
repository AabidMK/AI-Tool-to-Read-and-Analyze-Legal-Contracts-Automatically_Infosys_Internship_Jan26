import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retrieval_node import retrieve_clauses

query = "What happens if a shareholder wants to sell shares?"

results = retrieve_clauses(
    query=query,
    contract_type="Shareholder Agreement"
)

print("\nRetrieved Clauses:\n")

for r in results:
    print(r.page_content)
    print("Metadata:", r.metadata)
    print("-" * 50)
