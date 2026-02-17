import os
import traceback
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from api.storage import complete_task, fail_task
from pipeline.langgraph_pipeline import run_langgraph_pipeline


def run_contract_analysis(task_id: str, file_path: str):
    """
    Background task that:
    1. Runs LangGraph pipeline
    2. Stores final report
    3. Generates PDF
    4. Updates task status
    """

    try:
        print("Executing graph...")

        pipeline_output = run_langgraph_pipeline(file_path)

        if not isinstance(pipeline_output, dict):
            raise ValueError("Pipeline did not return a dictionary")

        if "final_report" not in pipeline_output:
            raise ValueError("Pipeline output missing 'final_report'")

        final_report = pipeline_output["final_report"]

        if not isinstance(final_report, str):
            raise ValueError("final_report is not a string")



        if not final_report:
            raise ValueError("Pipeline returned empty report")

        # 🔹 Print to terminal
        print("\n" + "=" * 100)
        print(f"FINAL CONTRACT REVIEW REPORT (Task ID: {task_id})")
        print("=" * 100)
        print(final_report)
        print("=" * 100 + "\n")

        # 🔹 Save PDF
        os.makedirs("generated_reports", exist_ok=True)

        pdf_filename = f"ClauseAI_Report_{task_id}.pdf"
        pdf_path = os.path.join("generated_reports", pdf_filename)

        generate_pdf(final_report, pdf_path)

        # 🔹 Mark task complete
        complete_task(task_id, final_report, pdf_path)

        print("Task completed successfully.")

    except Exception as e:
        print("Error during analysis:", str(e))
        traceback.print_exc()

        fail_task(task_id, str(e))


# ============================================================
# PDF GENERATION FUNCTION (Clean Professional Version)
# ============================================================

def generate_pdf(final_report: str, pdf_path: str):

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )

    normal_style = styles['Normal']

    # 🔹 Main Title (Always Added)
    elements.append(Paragraph("FINAL CONTRACT REVIEW REPORT", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    lines = final_report.split("\n")

    for line in lines:

        clean_line = (
            line.replace("**", "")
                .replace("###", "")
                .replace("####", "")
                .strip()
        )

        if not clean_line:
            elements.append(Spacer(1, 0.15 * inch))
            continue

        if line.startswith("###"):
            elements.append(Paragraph(clean_line, section_style))
        elif line.startswith("####"):
            elements.append(Paragraph(clean_line, styles["Heading3"]))
        else:
            elements.append(Paragraph(clean_line, normal_style))

        elements.append(Spacer(1, 0.12 * inch))

    doc.build(elements)
