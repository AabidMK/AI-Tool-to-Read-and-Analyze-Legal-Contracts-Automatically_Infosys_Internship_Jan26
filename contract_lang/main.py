from graph import build_graph
from vector_store import init_vector_db

if __name__ == "__main__":
    # Run once (comment after first run)
    init_vector_db()

    state = {
        "file_path": "input_files/agreement.docx"
    }

    build_graph(state)
