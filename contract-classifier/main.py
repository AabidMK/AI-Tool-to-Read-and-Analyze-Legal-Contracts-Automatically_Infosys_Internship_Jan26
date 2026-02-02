import json
from graph.classification_graph import build_graph
from parser.document_parser import parse_document
from retrieval import retrieve_similar_clauses

def extract_json(text: str) -> dict:
    if "```json" in text:
        start = text.find("```json") + len("```json")
        end = text.find("```", start)
        text = text[start:end]
    elif "```" in text:
        start = text.find("```") + len("```")
        end = text.find("```", start)
        text = text[start:end]
    
    return json.loads(text.strip())

def main():
    file_path = "sample_contracts/NondisclosureAgreement.pdf"
    contract_text = parse_document(file_path)
    
    print(f"Parsed document length: {len(contract_text)} characters")
    print(f"First 500 characters of parsed text:\n{contract_text[:500]}\n")
    
    contract_text_for_llm = contract_text[:12000]
    
    # First get classification
    graph = build_graph()
    result = graph.invoke({"contract_text": contract_text_for_llm})
    
    classification = result["classification"]
    print(f"Classification Result:\n{json.dumps(classification, indent=2)}\n")
    
    contract_type = classification.get("contract_type", "Unknown")
    
    # Retrieve clauses
    if contract_type != "Unknown":
        query = f"clauses related to {contract_type}"
        retrieved_clauses = retrieve_similar_clauses(
            query=query,
            contract_type=contract_type,
            top_k=3
        )
        
        print(f"Retrieved {len(retrieved_clauses)} relevant clauses:")
        print("=" * 80)
        
        for i, clause in enumerate(retrieved_clauses, 1):
            print(f"{i}. {clause['clause_title']} (Score: {clause['score']:.3f})")
            print(f"   Jurisdiction: {clause['jurisdiction']}")
            print(f"   Text: {clause['clause_text'][:200]}...")
            print()
    else:
        retrieved_clauses = []
        print("Retrieved 0 relevant clauses:")
        print("=" * 80)
    
    # Run analysis with retrieved clauses
    analysis_result = graph.invoke({
        "contract_text": contract_text_for_llm,
        "retrieved_clauses": retrieved_clauses
    })
    
    analysis = analysis_result.get("analysis", {})
    
    final_result = {
        **classification,
        "retrieved_clauses": retrieved_clauses,
        "analysis": analysis
    }
    
    print(f"Contract Analysis:")
    print("=" * 80)
    if analysis.get("analyzed_clauses"):
        for clause in analysis["analyzed_clauses"]:
            status = "Present" if clause.get("present") else "Missing"
            print(f"{clause.get('clause_title')}: {status}")
    
    print(f"\nFinal Result:")
    print("=" * 80)
    print(json.dumps(final_result, indent=2))
    
    with open("classification_result.json", "w") as f:
        json.dump(final_result, f, indent=2)
    
    with open("classification_result.txt", "w") as f:
        f.write(f"Contract Classification & Analysis Result\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Contract Type: {final_result.get('contract_type', 'Unknown')}\n")
        f.write(f"Industry: {final_result.get('industry', 'Unknown')}\n\n")
        
        if final_result.get('data'):
            f.write("Extracted Data:\n")
            for item in final_result['data']:
                f.write(f"- {item.get('name', 'Unknown')}: {item.get('value', 'Unknown')}\n")
        
        if analysis.get("analyzed_clauses"):
            f.write(f"\nClause Analysis:\n")
            for clause in analysis["analyzed_clauses"]:
                status = "Present" if clause.get("present") else "Missing"
                f.write(f"- {clause.get('clause_title')}: {status}\n")
        
        if retrieved_clauses:
            f.write(f"\nRetrieved Clauses ({len(retrieved_clauses)}):\n")
            for i, clause in enumerate(retrieved_clauses, 1):
                f.write(f"{i}. {clause['clause_title']} (Score: {clause['score']:.3f})\n")
                f.write(f"   {clause['clause_text'][:200]}...\n\n")
    
    print("Saved to classification_result.json and classification_result.txt")

if __name__ == "__main__":
    main()
