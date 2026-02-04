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
    
    # Get classification first
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
        print(f"Retrieved {len(retrieved_clauses)} relevant clauses")
    else:
        retrieved_clauses = []
        print("Retrieved 0 relevant clauses")
    
    # Run complete analysis pipeline
    final_result = graph.invoke({
        "contract_text": contract_text_for_llm,
        "retrieved_clauses": retrieved_clauses
    })
    
    # Extract final report
    final_report = final_result.get("final_report", {})
    
    print(f"\nFinal Contract Review Report:")
    print("=" * 80)
    print(f"Contract Type: {final_report.get('contract_summary', {}).get('type', 'Unknown')}")
    print(f"Industry: {final_report.get('contract_summary', {}).get('industry', 'Unknown')}")
    print(f"Overall Risk: {final_report.get('contract_summary', {}).get('overall_risk_rating', 'Unknown')}")
    print(f"Expert Analyses: {len(final_report.get('expert_analyses', []))}")
    print(f"Total Risks: {final_report.get('consolidated_findings', {}).get('total_risks_identified', 0)}")
    print(f"\nExecutive Summary:")
    print(final_report.get('executive_summary', 'No summary available'))
    
    # Save results
    with open("contract_review_report.json", "w") as f:
        json.dump(final_report, f, indent=2)
    
    # Generate markdown report
    with open("contract_review_report.md", "w") as f:
        f.write("# Comprehensive Contract Review Report\n\n")
        
        summary = final_report.get('contract_summary', {})
        f.write("## Contract Summary\n\n")
        f.write(f"- **Contract Type:** {summary.get('type', 'Unknown')}\n")
        f.write(f"- **Industry:** {summary.get('industry', 'Unknown')}\n")
        f.write(f"- **Overall Risk Rating:** {summary.get('overall_risk_rating', 'Unknown')}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write(f"{final_report.get('executive_summary', 'No summary available')}\n\n")
        
        # Missing clauses section
        missing_clauses = [clause for clause in final_report.get('clause_analysis', []) if not clause.get('present', True)]
        if missing_clauses:
            f.write("## Missing Clauses\n\n")
            for i, clause in enumerate(missing_clauses, 1):
                f.write(f"### {i}. {clause.get('clause_title', 'Unknown Clause')}\n\n")
                f.write(f"**Status:** Not Present\n\n")
                if clause.get('clause_text'):
                    f.write(f"**Recommended Text:**\n```\n{clause.get('clause_text')}\n```\n\n")
                metadata = clause.get('metadata', {})
                if metadata:
                    f.write(f"**Metadata:**\n")
                    f.write(f"- Jurisdiction: {metadata.get('jurisdiction', 'N/A')}\n")
                    f.write(f"- Version: {metadata.get('version', 'N/A')}\n")
                    f.write(f"- Last Updated: {metadata.get('last_updated', 'N/A')}\n\n")
        else:
            f.write("## Missing Clauses\n\n")
            f.write("✅ All recommended clauses are present in the contract.\n\n")
        
        f.write("## Expert Analyses\n\n")
        for i, analysis in enumerate(final_report.get('expert_analyses', []), 1):
            f.write(f"### {i}. {analysis.get('role', 'Unknown Role')}\n\n")
            f.write(f"**Rating:** {analysis.get('rating', 'No Rating')}\n\n")
            
            key_findings = analysis.get('key_findings', [])
            if key_findings:
                f.write("**Key Findings:**\n")
                for finding in key_findings:
                    f.write(f"- {finding}\n")
                f.write("\n")
            
            risks = analysis.get('risks', [])
            if risks:
                f.write("**Risks:**\n")
                for risk in risks:
                    f.write(f"- {risk}\n")
                f.write("\n")
            
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                f.write("**Recommendations:**\n")
                for rec in recommendations:
                    f.write(f"- {rec}\n")
                f.write("\n")
        
        findings = final_report.get('consolidated_findings', {})
        f.write("## Consolidated Findings\n\n")
        f.write(f"- **Total Risks Identified:** {findings.get('total_risks_identified', 0)}\n")
        f.write(f"- **Critical Compliance Issues:** {findings.get('critical_compliance_issues', 0)}\n")
        f.write(f"- **Key Recommendations:** {len(findings.get('key_recommendations', []))}\n\n")
        
        key_recs = findings.get('key_recommendations', [])
        if key_recs:
            f.write("### Top Recommendations\n\n")
            for i, rec in enumerate(key_recs, 1):
                f.write(f"{i}. {rec}\n")
    
    print("Saved complete report to contract_review_report.json and contract_review_report.md")

if __name__ == "__main__":
    main()
