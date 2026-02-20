import json
from pathlib import Path
from vectordb.client import get_vector_collection

def ingest_clause_library():

    collection = get_vector_collection()

    json_path = Path(r"data\clause_library\clause_example.json")
    clause_data = json.loads(json_path.read_text(encoding="utf-8"))

    total_count = 0

    for block in clause_data:
        contract_type = block["contract_type"]

        for idx,clause in enumerate(block["clauses"]):
            clause_title = clause["clause_title"]
            clause_text = clause["clause_text"]
            metadata_block = clause.get("metadata",{})

            document_text = f"{clause_title}\n{clause_text}"

            metadata = {
                "contract_type":contract_type,
                "clause_title":clause_title,
                "jurisdiction":metadata_block.get("jurisdiction",""),
                "version":metadata_block.get("version","")
            }

            clause_id = f"{contract_type}_{idx}"

            collection.add(
                ids=[clause_id],
                documents=document_text,
                metadatas=[metadata]
            )

            total_count +=1

    print(f"Total clauses indexed: {total_count}")