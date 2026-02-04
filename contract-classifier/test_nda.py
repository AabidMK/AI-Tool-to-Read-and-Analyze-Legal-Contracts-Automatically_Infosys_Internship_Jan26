import json
from graph.classification_graph import build_graph

def main():
    # Your NDA text
    contract_text = """
STQC Directorate,  
Ministry of Electronics & Information Technology,  
Electronics Niketan, 6 CGO Complex, Lodi Road,  
New Delhi – 110003.  

NON-DISCLOSURE AGREEMENT  

(Between STQC empaneled Auditor & Auditee)  

THIS NON-DISCLOSURE AGREEMENT is made on this …….. Day (date) of………… 
(Year) By and between:

STQC Directorate, Ministry of Electronics & Information Technology, 
Electronics Niketan, 6 CGO Complex, Lodi Road, New Delhi – 110003 
(hereinafter referred to as "STQC")

AND

[Auditee Company Name and Address]
(hereinafter referred to as "Auditee")

WHEREAS, STQC and Auditee wish to engage in discussions regarding 
confidential information for audit purposes;

NOW, THEREFORE, the parties agree as follows:

1. CONFIDENTIAL INFORMATION
All information disclosed by either party shall be considered confidential.

2. NON-DISCLOSURE
Neither party shall disclose confidential information to third parties.

3. TERM
This agreement shall remain in effect for a period of [X] years.
"""
    
    print("Analyzing NDA contract...")
    print("=" * 50)
    
    # Build and run the graph
    graph = build_graph()
    result = graph.invoke({"contract_text": contract_text})
    
    # Print results
    final_report = result.get("final_report", {})
    
    print("ANALYSIS COMPLETE")
    print("=" * 50)
    
    summary = final_report.get('contract_summary', {})
    print(f"Contract Type: {summary.get('type', 'Unknown')}")
    print(f"Industry: {summary.get('industry', 'Unknown')}")
    print(f"Risk Rating: {summary.get('overall_risk_rating', 'Unknown')}")
    
    print(f"\nExpert Analyses: {len(final_report.get('expert_analyses', []))}")
    for i, analysis in enumerate(final_report.get('expert_analyses', []), 1):
        print(f"{i}. {analysis.get('role', 'Unknown')} - {analysis.get('rating', 'No Rating')}")
    
    print(f"\nExecutive Summary:")
    print(final_report.get('executive_summary', 'No summary available'))
    
    # Save results
    with open("nda_analysis_report.json", "w") as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n✓ Full report saved to nda_analysis_report.json")

if __name__ == "__main__":
    main()
