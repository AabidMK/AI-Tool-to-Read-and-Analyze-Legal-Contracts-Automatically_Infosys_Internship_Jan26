"""
Vector Database module using ChromaDB for storing and querying embeddings.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import json


class VectorDatabase:
    """Vector database wrapper using ChromaDB for similarity search."""
    
    def __init__(self, collection_name: str = "contract_clauses", persist_directory: str = "./chroma_db"):
        """
        Initialize the vector database.
        
        Args:
            collection_name: Name of the collection to create/use
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        print(f"Initialized ChromaDB at: {persist_directory}")
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Contract clause embeddings"}
            )
            print(f"Created new collection: {collection_name}")
    
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents with their embeddings to the vector database.
        
        Args:
            ids: List of unique IDs for each document
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
        """
        if metadatas is None:
            metadatas = [{} for _ in ids]
        
        processed_metadatas = []
        for metadata in metadatas:
            processed_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (dict, list)):
                    processed_metadata[key] = json.dumps(value)
                else:
                    processed_metadata[key] = str(value)
            processed_metadatas.append(processed_metadata)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=processed_metadatas
        )
        
        print(f"Added {len(ids)} documents to the vector database")
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database for similar documents.
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary containing query results
        """
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        return results
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Integer count of documents
        """
        return self.collection.count()
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def reset_collection(self) -> None:
        """Reset the collection by deleting and recreating it."""
        try:
            self.delete_collection()
        except Exception:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Contract clause embeddings"}
        )
        print(f"Reset collection: {self.collection_name}")