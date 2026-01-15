# main.py
from graph import build_graph

if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "file_path": "sample_contract.pdf"
    })

    print("Classification Result:")
    print(result["classification"])
