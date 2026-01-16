from langchain_core.prompts import PromptTemplate

classification_prompt = PromptTemplate(
    input_variables=["contract_text"],
    template="""You are a legal document classifier. Analyze the contract and identify its type and industry. Return ONLY valid JSON in the following format:

{{
  "contract_type": "<contract type, e.g., Non-Disclosure Agreement, Service Agreement, Employment Agreement, etc.>",
  "industry": "<industry sector, e.g., IT, Healthcare, Finance, Manufacturing, Legal, etc.>"
}}

IMPORTANT: 
- Analyze the contract text carefully to identify the contract type
- Determine the industry sector this contract relates to
- Return ONLY the JSON object, no additional text or explanation
- Ensure all JSON is properly formatted and valid

Contract Text:
{contract_text}"""
)
