from pathlib import Path
from classification.graph import build_graph

md_files = sorted(
    Path("parser/outputs").glob("*.md"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

if not md_files:
    raise FileNotFoundError("No markdown files found in parser/outputs")

md_path = md_files[0]  # latest file

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

graph = build_graph()
result = graph.invoke({"markdown_text": md_text})

print(f"Classified file: {md_path.name}")
print(result["classification"])
