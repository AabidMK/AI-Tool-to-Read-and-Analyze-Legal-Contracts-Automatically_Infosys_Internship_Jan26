from docling.document_converter import DocumentConverter

converter = DocumentConverter()
file_path = "./NDA.pdf"

result = converter.convert(file_path)

if result.errors:
    print("❌ Errors during document conversion:")
    for error in result.errors:
        print(error)
    exit(1)

doc = result.document
legal_text = doc.export_to_text()

print("\n📄 Extracted Text:\n")
print(legal_text)


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSyAP_wKdt48uO6iUtvf5qWn1gpDajtVAukk"
)

prompt = ChatPromptTemplate.from_template(
    """
You are a legal document classification expert.
Return ONLY valid JSON.

Format:
{{
  "agreement_type": "...",
  "industry": "..."
}}

If unclear, use:
"Unknown Agreement"
"Unknown Industry"

Document:
\"\"\"
{legal_text}
\"\"\"
"""
)

parser = JsonOutputParser()
chain = prompt | llm | parser

result = chain.invoke({"legal_text": legal_text})

agreement_type = result.get("agreement_type")
industry = result.get("industry")

print("\n📊 Classification Result:")
print(result)
print("\nAgreement Type:", agreement_type)
print("Industry:", industry)


import json
import chromadb
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client()

clause_collection = chroma_client.get_or_create_collection(
    name="legal_clauses"
)

def ingest_clauses():
    with open("clause.json", "r") as f:
        clauses = json.load(f)

    documents, metadatas, ids = [], [], []

    for c in clauses:
        documents.append(c["clause_text"])
        ids.append(c["clause_id"])
        metadatas.append({
            "contract_type": c["contract_type"],
            "clause_title": c["clause_title"],
            "jurisdiction": c["jurisdiction"]
        })

    embeddings = embedding_model.encode(documents).tolist()

    clause_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print("✅ Clause ingestion complete")

if clause_collection.count() == 0:
    ingest_clauses()
else:
    print("ℹ️ Clauses already ingested")

def retrieve_relevant_clauses(
    document_text: str,
    agreement_type: str,
    top_k: int = 5
):
    query_embedding = embedding_model.encode(document_text).tolist()

    results = clause_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"contract_type": agreement_type}
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "clause_id": results["ids"][0][i],
            "clause_title": results["metadatas"][0][i]["clause_title"],
            "clause_text": results["documents"][0][i]
        })

    return retrieved


if agreement_type and agreement_type != "Unknown Agreement":
    retrieved_clauses = retrieve_relevant_clauses(
        document_text=legal_text,
        agreement_type=agreement_type,
        top_k=5
    )

    print("\n🔍 Retrieved Relevant Standard Clauses:\n")

    for clause in retrieved_clauses:
        print(f"📌 {clause['clause_title']}")
        print(clause["clause_text"])
        print("-" * 70)
else:
    print("⚠️ Agreement type unknown — retrieval skipped")
