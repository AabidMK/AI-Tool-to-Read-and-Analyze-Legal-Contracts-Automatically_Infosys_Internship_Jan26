from pathlib import Path
import chromadb
from chromadb.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PERSIST_DIR = PROJECT_ROOT / "vector_store"

COLLECTION_NAME = "contract_clauses"


def get_client():
    return chromadb.Client(
        Settings(
            persist_directory=str(PERSIST_DIR),
            anonymized_telemetry=False
        )
    )