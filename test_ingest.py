from vectordb.ingest import ingest_clause_library
from vectordb.client import get_vector_collection

ingest_clause_library()

collection = get_vector_collection()

print("Collection count:", collection.count())
