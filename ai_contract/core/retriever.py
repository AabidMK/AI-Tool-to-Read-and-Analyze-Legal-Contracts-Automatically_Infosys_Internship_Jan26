"""
Retriever module for similarity-based clause retrieval.
"""

from typing import List, Dict, Any, Optional
from .embedder import ClauseEmbedder
from .vector_db import VectorDatabase


class ClauseRetriever:
    """Handles similarity-based retrieval of contract clauses."""
    
    def __init__(self, embedder: ClauseEmbedder, vector_db: VectorDatabase):
        """
        Initialize the retriever with embedder and vector database.
        
        Args:
            embedder: ClauseEmbedder instance for generating query embeddings
            vector_db: VectorDatabase instance for similarity search
        """
        self.embedder = embedder
        self.vector_db = vector_db
        print("ClauseRetriever initialized")
    
    def retrieve(
        self,
        query: str,
        contract_type: Optional[str] = None,
        top_k: int = 5,
        category: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant clauses based on similarity search.
        
        Args:
            query: The search query text
            contract_type: Optional filter for specific contract type
            top_k: Number of top results to return
            category: Optional filter for clause category
            risk_level: Optional filter for risk level
            
        Returns:
            List of dictionaries containing retrieved clauses with metadata and scores
        """
        # Generate embedding for the query
        query_embedding = self.embedder.embed_text(query)
        
        # Build metadata filter
        where_filter = {}
        if contract_type:
            where_filter["contract_type"] = contract_type
        if category:
            where_filter["category"] = category
        if risk_level:
            where_filter["risk_level"] = risk_level
        
        # Perform similarity search
        results = self.vector_db.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        # Format results
        formatted_results = self._format_results(results)
        
        return formatted_results
    
    def retrieve_by_contract_type(
        self,
        query: str,
        contract_type: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve clauses filtered by specific contract type.
        
        Args:
            query: The search query text
            contract_type: Contract type to filter by
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing retrieved clauses
        """
        return self.retrieve(
            query=query,
            contract_type=contract_type,
            top_k=top_k
        )
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format raw ChromaDB results into structured output.
        
        Args:
            results: Raw results from ChromaDB query
            
        Returns:
            List of formatted result dictionaries
        """
        formatted = []
        
        if not results or not results.get('ids'):
            return formatted
        
        ids = results['ids'][0] if results['ids'] else []
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        for i in range(len(ids)):
            similarity_score = 1 - distances[i] if distances else 0
            
            formatted.append({
                "id": ids[i],
                "clause_text": documents[i],
                "metadata": metadatas[i] if metadatas else {},
                "similarity_score": round(similarity_score, 4),
                "distance": round(distances[i], 4) if distances else 0
            })
        
        return formatted
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary with database statistics
        """
        total_count = self.vector_db.get_collection_count()
        
        return {
            "total_clauses": total_count,
            "collection_name": self.vector_db.collection_name,
            "embedding_dimension": self.embedder.get_embedding_dimension()
        }