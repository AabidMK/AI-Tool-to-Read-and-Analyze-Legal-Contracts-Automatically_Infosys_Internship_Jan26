# AI Contract Classifier with Clause Retrieval

Automatically classifies legal contracts and retrieves similar clauses using AI. Uses local LLM classification with LM Studio embeddings and Qdrant vector search.

## Architecture

```
PDF Contract → Parse → Classify (Phi-3 Mini) → Retrieve Clauses (LM Studio + Qdrant) → Enhanced Results
```

## Requirements

- **Qdrant** (vector database)
- **LM Studio** (local embeddings server)
- **Ollama** (for Phi-3 Mini classification model)
- **Python 3.8+**

## Setup

### 1. Start Services

```bash
# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# Start LM Studio server on port 1234 with embedding model:
# text-embedding-embeddinggemma-300m-qat

# Install Ollama and pull model
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3:mini
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults should work)
```

### 4. Ingest Clauses

```bash
python ingestion.py
```

### 5. Verify Setup

```bash
python verify_ingestion.py
```

### 6. Run Classification

```bash
python main.py
```

## Output Example

```json
{
  "contract_type": "Non-Disclosure Agreement (NDA)",
  "industry": "Technology",
  "retrieved_clauses": [
    {
      "clause_title": "Definition of Confidential Information",
      "clause_text": "Confidential Information means...",
      "jurisdiction": "Global/Standard",
      "version": "1.0",
      "score": 0.89
    }
  ]
}
```

## Project Structure

```
contract-classifier/
├── main.py                    # Main pipeline
├── ingestion.py              # Load clauses into Qdrant
├── retrieval.py              # Similarity search
├── verify_ingestion.py       # Verify setup
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── clause.json              # Clause knowledge base
├── sample_contracts/        # Test contracts
├── graph/                   # Classification logic
├── parser/                  # Document parsing
└── prompts/                 # LLM prompts
```

## Troubleshooting

**Qdrant not running?**
```bash
docker ps
docker start qdrant
```

**LM Studio not responding?**
- Ensure server is running on port 1234
- Load the embedding model: `text-embedding-embeddinggemma-300m-qat`

**No clauses retrieved?**
- Check contract_type matches exactly in clause.json
- Verify ingestion completed successfully
