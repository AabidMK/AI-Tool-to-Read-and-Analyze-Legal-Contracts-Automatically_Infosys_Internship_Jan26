import json
from parser.document_parser import parse_document
from graph.classification_graph import build_graph

def main():
    # Provide your contract PDF or DOCX file path here
    file_path = "/Users/lakshanagopu/Desktop/AI/AI-Tool-to-Read-and-Analyze-Legal-Contracts-Automatically_Infosys_Internship_Jan26/contract-classifier/NondisclosureAgreement.pdf"
    
    print("=" * 60)
    print("Contract Classification System")
    print("=" * 60)
    print(f"\nProcessing document: {file_path}")
    
    # Extract content from the document
    contract_text = parse_document(file_path)
    
    print(f"✓ Document parsed successfully")
    print(f"✓ Document length: {len(contract_text)} characters")
    print(f"\nFirst 300 characters of extracted text:")
    print("-" * 60)
    print(contract_text[:300] + "..." if len(contract_text) > 300 else contract_text)
    print("-" * 60)
    print("\nSending to LLM for classification...\n")

    # Build and invoke the classification graph
    graph = build_graph()
    result = graph.invoke({
        "contract_text": contract_text
    })

    classification_output = result["classification"]
    
    # Handle both dict (from Pydantic parser) and string (raw LLM response) cases
    try:
        if isinstance(classification_output, dict):
            # Already a dict from Pydantic parser
            classification_json = classification_output
        elif isinstance(classification_output, str):
            # Extract JSON if it's wrapped in markdown code blocks or other text
            json_str = classification_output
            if "```json" in json_str:
                json_start = json_str.find("```json") + 7
                json_end = json_str.find("```", json_start)
                json_str = json_str[json_start:json_end].strip()
            elif "```" in json_str:
                json_start = json_str.find("```") + 3
                json_end = json_str.find("```", json_start)
                json_str = json_str[json_start:json_end].strip()
            
            # Parse JSON string
            classification_json = json.loads(json_str)
        else:
            # Convert other types to dict if possible
            classification_json = dict(classification_output) if hasattr(classification_output, '__dict__') else classification_output
        
        # Format and display
        formatted_output = json.dumps(classification_json, indent=2)
        
        print("=" * 60)
        print("Classification Result:")
        print("=" * 60)
        print(formatted_output)
        print("=" * 60)
        
        # Extract and display key information
        contract_type = classification_json.get("contract_type", "Unknown")
        industry = classification_json.get("industry", "Unknown")
        
        print(f"\n📄 Contract Type: {contract_type}")
        print(f"🏢 Industry: {industry}\n")
        
        # Save as both JSON and text
        with open("classification_result.json", "w") as f:
            json.dump(classification_json, f, indent=2)
        
        with open("classification_result.txt", "w") as f:
            f.write(formatted_output)
        
        print("✓ Results saved to:")
        print("  - classification_result.json")
        print("  - classification_result.txt")
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print("Warning: Could not process classification response")
        print(f"Response type: {type(classification_output)}")
        print(f"Raw response:\n{classification_output}")
        print(f"\nError: {e}")
        
        # Save raw output anyway
        with open("classification_result.txt", "w") as f:
            if isinstance(classification_output, str):
                f.write(classification_output)
            else:
                f.write(str(classification_output))
        print("Raw response saved to classification_result.txt")

if __name__ == "__main__":
    main()
