import os
import json
from graph import build_graph

INPUT_FILE = "input_files/rental_agreement.docx"
OUTPUT_DIR = "output_files"

os.makedirs(OUTPUT_DIR, exist_ok=True)

app = build_graph()

result = app.invoke({
    "file_path": INPUT_FILE
})

output_path = os.path.join(OUTPUT_DIR, "classification.json")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(result["classification"])

print("✅ Classification Done")
print(result["classification"])
