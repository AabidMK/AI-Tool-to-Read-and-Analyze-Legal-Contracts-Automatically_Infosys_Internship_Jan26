"""
Initializer module for loading clause data and initializing the vector database.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from core.embedder import ClauseEmbedder
from core.vector_db import VectorDatabase
from core.retriever import ClauseRetriever


class ClauseSystemInitializer:
    """Handles initialization of the contract clause system."""
    
    def __init__(
        self,
        clauses_file: str = "data/clauses.json",
        collection_name: str = "contract_clauses",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the system components.
        
        Args:
            clauses_file: Path to the clauses JSON file
            collection_name: Name for the vector database collection
            persist_directory: Directory to persist the vector database
            embedding_model: Name of the embedding model to use
        """
        self.clauses_file = clauses_file
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        
        self.embedder = None
        self.vector_db = None
        self.retriever = None
        self.clauses_data = []
    
    def load_clauses(self) -> List[Dict[str, Any]]:
        """
        Load clauses from the JSON file.
        
        Returns:
            List of clause dictionaries
        """
        print(f"\n{'='*60}")
        print(f"Loading clauses from: {self.clauses_file}")
        print(f"{'='*60}")
        
        clauses_path = Path(self.clauses_file)
        
        if not clauses_path.exists():
            raise FileNotFoundError(f"Clauses file not found: {self.clauses_file}")
        
        with open(clauses_path, 'r', encoding='utf-8') as f:
            self.clauses_data = json.load(f)
        
        print(f"✓ Loaded {len(self.clauses_data)} clauses")
        
        contract_types = {}
        for clause in self.clauses_data:
            contract_type = clause.get('contract_type', 'Unknown')
            contract_types[contract_type] = contract_types.get(contract_type, 0) + 1
        
        print(f"\nContract Types Distribution:")
        for contract_type, count in sorted(contract_types.items()):
            print(f"  - {contract_type}: {count} clauses")
        
        return self.clauses_data
    
    def initialize_embedder(self) -> ClauseEmbedder:
        """
        Initialize the embedding model.
        
        Returns:
            ClauseEmbedder instance
        """
        print(f"\n{'='*60}")
        print(f"Initializing Embedder")
        print(f"{'='*60}")
        
        self.embedder = ClauseEmbedder(model_name=self.embedding_model)
        return self.embedder
    
    def initialize_vector_db(self, reset: bool = False) -> VectorDatabase:
        """
        Initialize the vector database.
        
        Args:
            reset: Whether to reset the existing collection
            
        Returns:
            VectorDatabase instance
        """
        print(f"\n{'='*60}")
        print(f"Initializing Vector Database")
        print(f"{'='*60}")
        
        self.vector_db = VectorDatabase(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        if reset:
            print("Resetting collection...")
            self.vector_db.reset_collection()
        
        return self.vector_db
    
    def ingest_clauses(self) -> None:
        """Ingest clauses into the vector database with embeddings."""
        if not self.clauses_data:
            raise ValueError("No clauses loaded. Call load_clauses() first.")
        
        if not self.embedder:
            raise ValueError("Embedder not initialized. Call initialize_embedder() first.")
        
        if not self.vector_db:
            raise ValueError("Vector DB not initialized. Call initialize_vector_db() first.")
        
        print(f"\n{'='*60}")
        print(f"Ingesting Clauses into Vector Database")
        print(f"{'='*60}")
        
        ids = []
        documents = []
        metadatas = []
        
        for clause in self.clauses_data:
            document_text = f"{clause.get('clause_title', '')}: {clause.get('clause_text', '')}"
            
            ids.append(clause['id'])
            documents.append(document_text)
            
            metadata = {
                'contract_type': clause.get('contract_type', ''),
                'clause_title': clause.get('clause_title', ''),
                'category': clause.get('category', ''),
                'risk_level': clause.get('risk_level', ''),
            }
            
            if 'metadata' in clause and isinstance(clause['metadata'], dict):
                for key, value in clause['metadata'].items():
                    metadata[f'meta_{key}'] = str(value)
            
            metadatas.append(metadata)
        
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedder.embed_texts(documents)
        
        print(f"Adding documents to vector database...")
        self.vector_db.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✓ Successfully ingested {len(ids)} clauses")
        print(f"✓ Vector database now contains {self.vector_db.get_collection_count()} documents")
    
    def initialize_retriever(self) -> ClauseRetriever:
        """
        Initialize the clause retriever.
        
        Returns:
            ClauseRetriever instance
        """
        if not self.embedder:
            raise ValueError("Embedder not initialized. Call initialize_embedder() first.")
        
        if not self.vector_db:
            raise ValueError("Vector DB not initialized. Call initialize_vector_db() first.")
        
        print(f"\n{'='*60}")
        print(f"Initializing Retriever")
        print(f"{'='*60}")
        
        self.retriever = ClauseRetriever(
            embedder=self.embedder,
            vector_db=self.vector_db
        )
        
        return self.retriever
    
    def initialize_full_system(self, reset_db: bool = False) -> ClauseRetriever:
        """
        Initialize the complete system.
        
        Args:
            reset_db: Whether to reset the existing database
            
        Returns:
            ClauseRetriever instance ready for use
        """
        print(f"\n{'#'*60}")
        print(f"# INITIALIZING CONTRACT CLAUSE AI SYSTEM")
        print(f"{'#'*60}\n")
        
        self.load_clauses()
        self.initialize_embedder()
        self.initialize_vector_db(reset=reset_db)
        
        current_count = self.vector_db.get_collection_count()
        if current_count == 0 or reset_db:
            print(f"\nVector database is empty or reset requested. Ingesting data...")
            self.ingest_clauses()
        else:
            print(f"\nVector database already contains {current_count} documents. Skipping ingestion.")
            print(f"(Use reset_db=True to re-ingest)")
        
        self.initialize_retriever()
        
        print(f"\n{'#'*60}")
        print(f"# SYSTEM INITIALIZATION COMPLETE")
        print(f"{'#'*60}\n")
        
        stats = self.retriever.get_statistics()
        print("System Statistics:")
        print(f"  - Total Clauses: {stats['total_clauses']}")
        print(f"  - Collection Name: {stats['collection_name']}")
        print(f"  - Embedding Dimension: {stats['embedding_dimension']}")
        print()
        
        return self.retriever