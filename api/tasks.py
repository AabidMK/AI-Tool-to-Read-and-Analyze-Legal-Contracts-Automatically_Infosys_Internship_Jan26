from pipeline.langgraph_pipeline import build_graph
from api.storage import complete_task, fail_task

graph = build_graph()


def run_contract_analysis(task_id: str, file_path: str):
    try:
        initial_state = {
            "input_file": file_path,
            "contract_text": "",
            "result": {},
            "matched_clauses": [],
            "review_plan": [],
            "role_analysis_results": [],
            "summarized_role_results": [],
            "final_report": ""
        }

        final_state = graph.invoke(initial_state)

        # 🔍 DEBUG: see role summaries in terminal
        print("\n=== ROLE SUMMARIES ===")
        for r in final_state["summarized_role_results"]:
            print(f"\nROLE: {r['role']}")
            print(r["summary"])
        print("=====================\n")

        complete_task(
            task_id,
            final_state["final_report"]
        )

    except Exception as e:
        fail_task(task_id, str(e))
