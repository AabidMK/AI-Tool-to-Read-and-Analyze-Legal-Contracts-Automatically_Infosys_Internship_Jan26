from pathlib import Path
from parser import parse_document

# Input file (PDF or DOCX)
input_file = "data/uploads/EX-10.1.docx"

# Output file
output_file = "data/parsed/EX-10.1_from_unified_parser.txt"

# Parse document
lines = parse_document(input_file)

# Ensure output directory exists
Path(output_file).parent.mkdir(parents=True, exist_ok=True)

# Save to .txt
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Parser test completed.")
print("Lines:", len(lines))
print("Characters:", len(" ".join(lines)))
