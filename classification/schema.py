from pydantic import BaseModel, Field

class ContractClassification(BaseModel):
    contract_type: str = Field(
        description="Type of contract (e.g., Employment Agreement, NDA, SaaS Agreement)"
    )
    industry: str = Field(
        description="Industry domain (e.g., IT, Finance, Healthcare, Government)"
    )