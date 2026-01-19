"""
Contract Classification System
Main entry point for classifying legal contracts.
"""

from pathlib import Path
from classifier import ContractClassifier
import json


def print_results(results: list):
    """Display classification results."""
    print("\n" + "-"*60)
    print("Classification Results")
    print("-"*60)
    
    for r in results:
        file_name = Path(r['file']).name
        
        if r['status'] == 'success':
            print(f"\nFile: {file_name}")
            print(f"  Type: {r['contract_type']}")
            print(f"  Industry: {r['industry']}")
        else:
            print(f"\nFile: {file_name}")
            print(f"  Status: ERROR - {r['error']}")
    
    print("\n" + "-"*60)
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Total: {len(results)} files | Success: {success_count}")
    print("-"*60)


def main():
    """Main function - Add your files to the list below."""
    
    print("Initializing classifier...")
    classifier = ContractClassifier()
    print("Ready.\n")
    
    files_to_classify = [
        'Legal-Notice-for-Recovery-of-Friendly-Loan-LawRato.docx',
        'SaaS and Services Agreement_.docx'
    ]
    
    #
    
    print(f"Classifying {len(files_to_classify)} file(s)...\n")
    
    # Classify all files
    results = classifier.classify_batch(files_to_classify)
    
    # Display results
    print_results(results)
    
    # Save to JSON
    output_file = 'classification_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
