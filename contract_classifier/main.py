from graph import app

if __name__ == "__main__":
    result = app.invoke({
        "file_path": r"C:\Users\HP\Desktop\springboard\contract_classifier\main_assignment-contract-agreement-template.pdf"  # <-- exact filename
    })

    print("\n--- Contract Classification ---")
    print(result["classification"])