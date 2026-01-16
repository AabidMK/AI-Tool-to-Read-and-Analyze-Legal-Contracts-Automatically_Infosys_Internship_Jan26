# Contract Classification System

A LangGraph and LangChain-based system for classifying legal contracts by extracting contract type and industry from PDF or DOCX documents.

## Overview

This system implements a **classification node** that:
- Takes a contract document (PDF or DOCX) as input
- Extracts text content from the document
- Sends the content to an LLM (Google Gemini) for analysis
- Returns the **contract type** and **industry** as structured JSON output

## Architecture

### Components

1. **Document Parser** (`parser/document_parser.py`)
   - Uses Docling to extract text from PDF/DOCX files
   - Converts documents to markdown format for LLM processing

2. **Classification Graph** (`graph/classification_graph.py`)
   - Implements a LangGraph state graph
   - Contains a classification node that processes contract text
   - Uses LangChain with Google Gemini LLM for classification (faster results)
   - Returns structured output using Pydantic models

3. **Main Entry Point** (`main.py`)
   - Orchestrates the document parsing and classification workflow
   - Handles output formatting and file saving

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Gemini API key:
```bash
# Option 1: Set environment variable
export GOOGLE_API_KEY="your-api-key-here"

# Option 2: Create a .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

**Note**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Alternative**: The code also supports Ollama (commented out). To use Ollama instead:
- Uncomment the Ollama lines in `classification_graph.py`
- Comment out the Gemini lines
- Ensure Ollama is running: `ollama serve`

## Usage

1. Place your contract PDF or DOCX file in the project directory

2. Update the file path in `main.py`:
```python
file_path = "path/to/your/contract.pdf"
```

3. Run the classification:
```bash
python main.py
```

## Output

The system generates two output files:

- **classification_result.json**: Structured JSON with contract type and industry
- **classification_result.txt**: Human-readable text version

### Output Format

```json
{
  "contract_type": "Non-Disclosure Agreement",
  "industry": "IT"
}
```

## Project Structure

```
contract-classifier/
├── main.py                      # Main entry point
├── parser/
│   └── document_parser.py      # Document extraction
├── graph/
│   └── classification_graph.py # LangGraph classification node
├── prompts/
│   └── classify_prompt.py      # LLM prompts (if used)
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Technologies Used

- **LangGraph**: For building the classification workflow graph
- **LangChain**: For LLM integration and prompt management
- **Google Gemini**: Cloud LLM for fast classification (gemini-pro model)
- **Docling**: Document parsing and text extraction
- **Pydantic**: Structured output validation

## Classification Node Details

The classification node (`classification_node` in `classification_graph.py`):

1. **Input**: Contract text (extracted from PDF/DOCX)
2. **Processing**: 
   - Truncates text to 8000 characters if needed
   - Sends to LLM with classification prompt
   - Parses structured JSON response
3. **Output**: Dictionary with `contract_type` and `industry`

## Example

```python
from parser.document_parser import parse_document
from graph.classification_graph import build_graph

# Parse document
contract_text = parse_document("contract.pdf")

# Build and invoke graph
graph = build_graph()
result = graph.invoke({"contract_text": contract_text})

# Access results
print(result["classification"]["contract_type"])
print(result["classification"]["industry"])
```

## Notes

- The system supports both PDF and DOCX file formats
- Document text is truncated to 8000 characters for LLM processing
- **Gemini API key required**: Set `GOOGLE_API_KEY` environment variable
- The model can be changed in `classification_graph.py` (line 25)
- Ollama code is commented out but available as an alternative
