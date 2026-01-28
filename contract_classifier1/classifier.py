from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

PERSIST_DIR = "contract_classifier1/vector_db/clauses"
COLLECTION_NAME = "contract_clauses"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are a legal expert.

The user query is:
{query}

We retrieved the following clauses:
{clauses}

Please summarize and classify the clauses, explaining which are most relevant to the query.
Return the output as JSON with keys:
- relevant_clauses: list of top clauses
- reasoning: short explanation
""")

def retrieve_and_reason(query: str, contract_type: str, top_k: int = 3):
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=OpenAIEmbeddings()
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": {"contract_type": contract_type}
        }
    )

    retrieved_docs = retriever.invoke(query)
    if not retrieved_docs:
        return '{"relevant_clauses": [], "reasoning": "No matching clauses found. Check contract_type and persist directory."}'

    clauses_text = "\n".join(doc.page_content for doc in retrieved_docs)

    chain = prompt | llm
    response = chain.invoke({
        "query": query,
        "clauses": clauses_text
    })

    return response.content

if __name__ == "__main__":
    query = "sharing confidential company information"
    contract_type = "Employment"

    print("🔍 Query:", query)
    print("📄 Contract Type:", contract_type)
    print("\n📌 LLM Processed Clauses:\n")
    print(retrieve_and_reason(query, contract_type))
