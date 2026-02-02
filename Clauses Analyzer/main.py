"""
Main: Contract Classification + Clause Retrieval + Analysis
"""

from classifier import classify_contract
import json

# Your contract file path
file_path = ".Memorandum-of-Understanding-MOU-LawRato3.docx"

print("="*70)
print("CONTRACT ANALYSIS SYSTEM")
print("="*70 + "\n")

# Run full workflow
result = classify_contract(file_path)

# Display results
print("\n" + "="*70)
print("CLASSIFICATION RESULTS")
print("="*70)
print(f"File: {result['file_path']}")
print(f"Contract Type: {result['contract_type']}")
print(f"Industry: {result['industry']}")

print("\n" + "="*70)
print("RETRIEVED CLAUSES")
print("="*70)
print(f"\nFound {len(result['clauses'])} relevant clauses:\n")

for i, clause in enumerate(result['clauses'][:3], 1):
    print(f"{i}. {clause['clause_title']} (relevance: {clause['score']:.3f})")
    print(f"   Type: {clause['contract_type']}")
    print(f"   {clause['clause_text'][:150]}...\n")

# Display analysis
if result['analysis']:
    print("="*70)
    print("CONTRACT ANALYSIS")
    print("="*70)
    
    analysis = result['analysis']
    
    print(f"\n🎯 Risk Level: {analysis['risk_level']}\n")
    
    print("📊 Contextual Analysis:")
    print(f"{analysis['contextual_analysis']}\n")
    
    print("💡 Suggestions for Improvement:")
    for i, suggestion in enumerate(analysis['suggestions'], 1):
        print(f"{i}. {suggestion}")
    
    print(f"\n⚠️  Missing Standard Clauses ({len(analysis['missing_clauses'])}):")
    for i, missing in enumerate(analysis['missing_clauses'], 1):
        print(f"{i}. {missing}")

# Save to JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print("✓ Full results saved to output.json")
print("="*70)
