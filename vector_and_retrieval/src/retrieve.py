from src.chroma_config import get_client, COLLECTION_NAME

client = get_client()
collection = client.get_collection(name=COLLECTION_NAME)


def retrieve_similar(query, contract_type, k=3):

    result = collection.query(
        query_texts=[query],
        n_results=k,
        where={"contract_type": contract_type}
    )

    clauses = []

    for i in range(len(result["documents"][0])):
        clauses.append({
            "text": result["documents"][0][i],
            "title": result["metadatas"][0][i]["title"]
        })

    return clauses