from vectorstore.chroma_store import load_chroma

vs = load_chroma()

all_meta = vs._collection.get(include=["metadatas"])["metadatas"]

unique_contract_types = sorted(set(m["contract_type"] for m in all_meta))
print(unique_contract_types)
