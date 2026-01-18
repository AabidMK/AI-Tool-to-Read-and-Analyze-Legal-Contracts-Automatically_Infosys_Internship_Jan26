from graph.classification_node import classification_node

file_path = "input_files_2/document.pdf"

result = classification_node(file_path)

print("\n✅ FINAL OUTPUT")
if "error" in result:
    print("❌ Error:", result["error"])
else:
    print("Contract Type :", result["contract_type"])
    print("Industry      :", result["industry"])
    print("Confidence    :", int(result["confidence"] * 100), "%")
