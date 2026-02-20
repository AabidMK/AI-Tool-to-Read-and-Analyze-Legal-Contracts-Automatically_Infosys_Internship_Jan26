import chromadb
from config.embeddings import get_embedding_function

def get_vector_collection():

    embedding_function = get_embedding_function()

    client= chromadb.PersistentClient(
        path= r"storage\vectorstore"
    )

    collection = client.get_or_create_collection(
        name= "clause_library",
        embedding_function= embedding_function
    )
    
    return collection