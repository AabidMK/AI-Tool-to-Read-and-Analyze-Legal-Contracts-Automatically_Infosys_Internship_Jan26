from dotenv import load_dotenv
load_dotenv()
from graph.graph_builder import build_graph


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "file_path": "inputs/cisco-master-data-protection-agreement.pdf"
    })

    print(result["classification"])
