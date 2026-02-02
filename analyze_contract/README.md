## Analyze Contract Node

### Description
The Analyze Contract node uses an LLM to review a contract by comparing it with similar standard clauses.

---

### What it does

- Contextual Analysis
  Compares the input contract text with retrieved reference clauses to understand differences and gaps.

- suggestion Engine*
  Provides suggestions to improve or refine the existing contract text.

- Omission Detection
  Identifies important clauses that are usually required for this contract type but are missing in the document.

---

### Input
- Contract document text  
- Relevant clauses retrieved from the vector database  

---

### Output
- Analysis of the contract content  
- Improvement suggestions  
- List of missing standard clauses  

---

### Purpose
Helps in quickly reviewing contracts and improving their completeness and quality using AI.
