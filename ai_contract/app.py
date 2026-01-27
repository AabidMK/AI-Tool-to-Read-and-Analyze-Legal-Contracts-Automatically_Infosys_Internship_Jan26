"""
Contract Clause AI System - Main Application
Uses LangGraph and LangChain for similarity-based clause retrieval.
"""

import json
from pathlib import Path
from services.initializer import ClauseSystemInitializer
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from core.retriever import ClauseRetriever


# LangGraph State Definition
class RetrievalState(TypedDict):
    """State definition for the retrieval workflow."""
    query: str
    contract_type: str
    top_k: int
    category: str
    risk_level: str
    retrieved_clauses: List[Dict[str, Any]]
    formatted_output: str
    messages: Annotated[List, "messages"]


class ClauseRetrievalGraph:
    """LangGraph workflow for contract clause retrieval."""
    
    def __init__(self, retriever: ClauseRetriever):
        self.retriever = retriever
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(RetrievalState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input_node)
        workflow.add_node("retrieve_clauses", self._retrieve_clauses_node)
        workflow.add_node("format_results", self._format_results_node)
        
        # Define edges
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "retrieve_clauses")
        workflow.add_edge("retrieve_clauses", "format_results")
        workflow.add_edge("format_results", END)
        
        return workflow.compile()
    
    def _validate_input_node(self, state: RetrievalState) -> RetrievalState:
        """Validate and process input parameters."""
        messages = state.get("messages", [])
        messages.append(HumanMessage(content=f"Validating query: {state.get('query', 'N/A')}"))
        
        if "top_k" not in state or state["top_k"] is None:
            state["top_k"] = 5
        if "contract_type" not in state or state["contract_type"] is None:
            state["contract_type"] = ""
        if "category" not in state or state["category"] is None:
            state["category"] = ""
        if "risk_level" not in state or state["risk_level"] is None:
            state["risk_level"] = ""
        
        messages.append(AIMessage(content="Input validation complete"))
        state["messages"] = messages
        return state
    
    def _retrieve_clauses_node(self, state: RetrievalState) -> RetrievalState:
        """Perform similarity search to retrieve relevant clauses."""
        messages = state.get("messages", [])
        
        contract_type = state["contract_type"] if state["contract_type"] else None
        category = state["category"] if state["category"] else None
        risk_level = state["risk_level"] if state["risk_level"] else None
        
        messages.append(AIMessage(
            content=f"Retrieving clauses - Type: {contract_type}, Category: {category}, Risk: {risk_level}"
        ))
        
        retrieved_clauses = self.retriever.retrieve(
            query=state["query"],
            contract_type=contract_type,
            top_k=state["top_k"],
            category=category,
            risk_level=risk_level
        )
        
        state["retrieved_clauses"] = retrieved_clauses
        messages.append(AIMessage(content=f"Retrieved {len(retrieved_clauses)} clauses"))
        state["messages"] = messages
        return state
    
    def _format_results_node(self, state: RetrievalState) -> RetrievalState:
        """Format the retrieved results for output."""
        messages = state.get("messages", [])
        clauses = state["retrieved_clauses"]
        
        output_lines = ["=" * 80, f"RETRIEVAL RESULTS FOR: {state['query']}", "=" * 80, ""]
        
        if state["contract_type"]:
            output_lines.append(f"Contract Type Filter: {state['contract_type']}")
        if state["category"]:
            output_lines.append(f"Category Filter: {state['category']}")
        if state["risk_level"]:
            output_lines.append(f"Risk Level Filter: {state['risk_level']}")
        
        output_lines.extend([f"Top {state['top_k']} Results", "", "=" * 80, ""])
        
        for i, clause in enumerate(clauses, 1):
            output_lines.extend([
                f"RESULT #{i}", "-" * 80,
                f"ID: {clause['id']}",
                f"Similarity Score: {clause['similarity_score']:.4f}",
                f"Distance: {clause['distance']:.4f}", "",
                "Metadata:"
            ])
            
            metadata = clause.get('metadata', {})
            output_lines.extend([
                f"  Contract Type: {metadata.get('contract_type', 'N/A')}",
                f"  Clause Title: {metadata.get('clause_title', 'N/A')}",
                f"  Category: {metadata.get('category', 'N/A')}",
                f"  Risk Level: {metadata.get('risk_level', 'N/A')}", "",
                "Clause Text:",
                clause['clause_text'], "", "=" * 80, ""
            ])
        
        if not clauses:
            output_lines.extend(["No clauses found matching the criteria.", ""])
        
        state["formatted_output"] = "\n".join(output_lines)
        messages.append(AIMessage(content="Results formatted successfully"))
        state["messages"] = messages
        return state
    
    def run(self, query: str, contract_type: str = "", top_k: int = 5,
            category: str = "", risk_level: str = "") -> Dict[str, Any]:
        """Execute the retrieval workflow."""
        initial_state = {
            "query": query,
            "contract_type": contract_type,
            "top_k": top_k,
            "category": category,
            "risk_level": risk_level,
            "retrieved_clauses": [],
            "formatted_output": "",
            "messages": []
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state


def save_results(results: dict, output_file: str = "outputs/results.json"):
    """Save retrieval results to a JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    serializable_results = {
        "query": results.get("query", ""),
        "contract_type": results.get("contract_type", ""),
        "top_k": results.get("top_k", 5),
        "category": results.get("category", ""),
        "risk_level": results.get("risk_level", ""),
        "retrieved_clauses": results.get("retrieved_clauses", [])
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {output_file}")


def main():
    """Main application entry point."""
    print("\n" + "#" * 80)
    print("#  CONTRACT CLAUSE AI SYSTEM")
    print("#  Powered by LangGraph, LangChain, and Vector Search")
    print("#" * 80 + "\n")
    
    # Initialize the system
    initializer = ClauseSystemInitializer(
        clauses_file="data/clauses.json",
        collection_name="contract_clauses",
        persist_directory="./chroma_db",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    retriever = initializer.initialize_full_system(reset_db=False)
    
    # Create LangGraph workflow
    print("\n" + "=" * 80)
    print("Creating LangGraph Workflow")
    print("=" * 80 + "\n")
    
    workflow = ClauseRetrievalGraph(retriever=retriever)
    print("✓ LangGraph workflow created successfully\n")
    
    # Example 1: NDA confidentiality
    print("#" * 80)
    print("# EXAMPLE 1: Finding confidentiality clauses in NDAs")
    print("#" * 80 + "\n")
    
    results1 = workflow.run(
        query="confidential information protection and disclosure restrictions",
        contract_type="NDA",
        top_k=3
    )
    print(results1["formatted_output"])
    save_results(results1, "outputs/example1_nda_confidentiality.json")
    
    # Example 2: SLA performance
    print("\n" + "#" * 80)
    print("# EXAMPLE 2: Finding performance guarantees in SLAs")
    print("#" * 80 + "\n")
    
    results2 = workflow.run(
        query="uptime guarantees and service availability commitments",
        contract_type="SLA",
        top_k=3
    )
    print(results2["formatted_output"])
    save_results(results2, "outputs/example2_sla_performance.json")
    
    # Example 3: Employment IP
    print("\n" + "#" * 80)
    print("# EXAMPLE 3: Finding IP clauses in Employment contracts")
    print("#" * 80 + "\n")
    
    results3 = workflow.run(
        query="intellectual property rights and ownership of inventions",
        contract_type="Employment",
        top_k=3
    )
    print(results3["formatted_output"])
    save_results(results3, "outputs/example3_employment_ip.json")
    
    print("\n" + "#" * 80)
    print("#  All examples completed successfully!")
    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()