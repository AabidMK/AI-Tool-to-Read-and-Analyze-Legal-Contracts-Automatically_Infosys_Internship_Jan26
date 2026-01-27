# Contract Clause AI System

Vector database-powered contract clause retrieval using **LangGraph** and **LangChain**.

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt --break-system-packages
```

### Run
```bash
python app.py
```

## 📁 Project Structure

```
contract_clause_ai/
│
├── app.py                     # 🚀 Main entry point (run this)
│
├── data/
│   └── clauses.json           # 12 sample contract clauses
│
├── core/
│   ├── __init__.py
│   ├── embedder.py            # Text → embeddings
│   ├── vector_db.py           # ChromaDB vector database
│   └── retriever.py           # Similarity-based retrieval
│
├── services/
│   ├── __init__.py
│   └── initializer.py         # System initialization & data ingestion
│
├── outputs/
│   └── results.json           # Query results
│
└── requirements.txt
```

## ✨ Features

### Vector Database Initialization
- **ChromaDB** for persistent vector storage
- **Sentence Transformers** (all-MiniLM-L6-v2) for embeddings
- Automatic collection creation and management
- Metadata filtering support

### Similarity-Based Retrieval Node
- **Cosine similarity** search
- **Contract type filtering** (NDA, SLA, Employment)
- **Category and risk level** filtering
- Top-k result ranking

### LangGraph Workflow
```
Validate Input → Retrieve Clauses → Format Results
```

## 📊 Data Format

**clauses.json** contains:
```json
{
  "id": "NDA-001",
  "contract_type": "NDA",
  "clause_title": "Confidentiality Obligation",
  "clause_text": "Full clause text...",
  "category": "confidentiality",
  "risk_level": "high",
  "metadata": {
    "jurisdiction": "US",
    "last_updated": "2024-01-15"
  }
}
```

## 💡 Usage Examples

### Example 1: Find NDA Confidentiality Clauses
```python
results = workflow.run(
    query="confidential information protection",
    contract_type="NDA",
    top_k=3
)
```

### Example 2: Find SLA Performance Clauses
```python
results = workflow.run(
    query="uptime guarantees and availability",
    contract_type="SLA",
    top_k=3
)
```

### Example 3: Find Employment IP Clauses
```python
results = workflow.run(
    query="intellectual property ownership",
    contract_type="Employment",
    top_k=3
)
```

## 🔧 How It Works

### 1. Vector Database Initialization
```python
# Load clauses from JSON
clauses = load_clauses("data/clauses.json")

# Generate embeddings
embeddings = embedder.embed_texts(clauses)

# Store in ChromaDB
vector_db.add_documents(ids, documents, embeddings, metadata)
```

### 2. Similarity-Based Retrieval
```python
# Embed query
query_embedding = embedder.embed_text(query)

# Search with filters
results = vector_db.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    where={"contract_type": "NDA"}
)

# Format and return
return format_results(results)
```

### 3. LangGraph Workflow
- **Node 1 (Validate)**: Normalize inputs and set defaults
- **Node 2 (Retrieve)**: Execute similarity search with filters
- **Node 3 (Format)**: Structure results for output

## 📈 Output Format

Results include:
- **ID**: Clause identifier
- **Similarity Score**: 0-1 (higher is better)
- **Distance**: ChromaDB cosine distance
- **Metadata**: Contract type, category, risk level
- **Clause Text**: Full clause content

## 🎯 Key Components

### ClauseEmbedder
- Converts text to 384-dimensional vectors
- Uses sentence-transformers
- Batch processing support

### VectorDatabase
- ChromaDB wrapper
- Metadata filtering
- Persistent storage

### ClauseRetriever
- Similarity search
- Multi-filter support
- Result formatting

### ClauseRetrievalGraph (LangGraph)
- State machine workflow
- Three-node pipeline
- Message tracking

## 🔍 Similarity Scoring

- **1.0**: Perfect match
- **0.9-1.0**: Very similar
- **0.7-0.9**: Similar
- **0.5-0.7**: Somewhat similar
- **< 0.5**: Not very similar

## 📝 Adding Your Own Clauses

1. Edit `data/clauses.json`
2. Add new clause objects
3. Run with `reset_db=True` in app.py:
   ```python
   retriever = initializer.initialize_full_system(reset_db=True)
   ```

## 🛠️ Troubleshooting

### Slow First Run
Model downloads (~80MB) on first run. Subsequent runs are fast.

### Reset Database
```python
# In app.py, change line:
retriever = initializer.initialize_full_system(reset_db=True)
```

## 📦 Dependencies

- **langchain**: LLM framework
- **langgraph**: Workflow orchestration  
- **chromadb**: Vector database
- **sentence-transformers**: Embeddings
- **numpy**: Numerical operations
- **pydantic**: Data validation

## 🎓 Learn More

- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **ChromaDB**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/

---

**Built with LangGraph, LangChain, and Vector Search** 🚀