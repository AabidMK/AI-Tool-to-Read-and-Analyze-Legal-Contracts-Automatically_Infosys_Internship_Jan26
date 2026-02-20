from pathlib import Path

from graphs.clause_analysis_graph import run_clause_analysis
from parser import parse_document
from report.generate import generate_final_report

from .storage import OUTPUT_DIR, TaskStatus, update_task


def execute_clause_analysis_task(task_id: str, file_path: Path, include_review: bool = True) -> None:
    update_task(task_id, status=TaskStatus.PROCESSING, stage="Parsing document")

    try:
        contract_lines = parse_document(str(file_path))
        contract_text = "\n".join(contract_lines)

        if include_review:
            update_task(task_id, stage="Running full analysis (with expert review)")
        else:
            update_task(task_id, stage="Running fast analysis (review skipped)")

        analysis_result = run_clause_analysis(contract_text, include_review=include_review)

        update_task(task_id, stage="Generating final report")
        final_report = generate_final_report(analysis_result)

        result_path = OUTPUT_DIR / f"{task_id}.txt"
        result_path.write_text(final_report, encoding="utf-8")

        update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            stage="Completed",
            result_path=str(result_path),
            error=None,
        )
    except Exception as exc:
        update_task(
            task_id,
            status=TaskStatus.FAILED,
            stage="Failed",
            result_path=None,
            error=str(exc),
        )