from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json

# ----- Pydantic Models for Structured Output -----
class ContractData(BaseModel):
    """Key data point from the contract"""
    name: str = Field(description="Name of the data field")
    value: str = Field(description="Value or content of the field")

class ContractClassification(BaseModel):
    """Contract classification with type, industry, and key data"""
    contract_type: str = Field(description="Type of contract (e.g., NDA, Service Agreement)")
    industry: str = Field(description="Industry sector (e.g., IT, Healthcare, Finance)")
    data: List[ContractData] = Field(description="Key data points extracted from contract")

# ----- Graph State -----
class GraphState(TypedDict):
    contract_text: str
    classification: dict

# ----- LLM with JSON mode -----
llm = OllamaLLM(model="tinyllama", temperature=0, format="json")

# ----- Output Parser -----
parser = JsonOutputParser(pydantic_object=ContractClassification)

# ----- Prompt -----
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal document analyzer. Extract contract type, industry, and key data points. Return ONLY valid JSON."),
    ("user", """Analyze this contract and extract:
1. Contract Type (e.g., NDA, Service Agreement, Employment Agreement)
2. Industry (e.g., IT, Healthcare, Finance)
3. Key data points like party names, obligations, exclusions, terms, etc.

Contract Text:
{contract_text}

{format_instructions}""")
])

prompt = prompt.partial(format_instructions=parser.get_format_instructions())

# ----- Node -----
def classification_node(state: GraphState) -> GraphState:
    # Use full contract text, but limit to reasonable size for LLM
    contract_text = state["contract_text"]
    # Increase limit to 8000 characters to capture more content
    if len(contract_text) > 8000:
        contract_text = contract_text[:8000] + "\n\n[Document truncated for length...]"
    
    # Create chain with parser
    chain = prompt | llm | parser
    response = chain.invoke({"contract_text": contract_text})
    
    # Convert Pydantic model to dict
    return {
        "classification": response.dict() if hasattr(response, 'dict') else response
    }

# ----- Graph -----
def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("classify_contract", classification_node)
    graph.set_entry_point("classify_contract")
    graph.set_finish_point("classify_contract")
    return graph.compile()

