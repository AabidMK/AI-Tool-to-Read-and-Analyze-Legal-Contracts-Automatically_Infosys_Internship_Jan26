from vectorstore.chroma_store import initialize_chroma

if __name__ == "__main__":
    vs = initialize_chroma()
    print("Ingested documents:", vs._collection.count())
