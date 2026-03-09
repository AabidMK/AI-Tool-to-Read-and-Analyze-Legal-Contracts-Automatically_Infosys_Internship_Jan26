from src.graph import app


def main():

    contract_text = """
This agreement defines services provided by the vendor.
The provider shall deliver software development services.
Payment terms shall be mutually agreed.
"""

    result = app.invoke({
        "document_text": contract_text,
        "contract_type": "Service Agreement",
        "industry": "Technology"
    })

    print("\n=========== FINAL REPORT ===========\n")
    print(result["final_report"])


if __name__ == "__main__":
    main()