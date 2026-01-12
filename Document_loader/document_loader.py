from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
# from langchain_community.llms import Ollama
# from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_community.document_loaders import Docx2txtLoader

load_dotenv()

loader_pdf=PyPDFLoader('Legal_document.pdf')
pdf=loader_pdf.load()


loader_doc= Docx2txtLoader('Legal_doc_2.docx')
docs=loader_doc.lazy_load()

loader_txt= TextLoader('The Count of Monte Cristo.txt', encoding='latin-1')
txt=loader_txt.load()


#print(docs[0].page_content)
#print(pdf)
#print(txt)

for i in docs:
    print(i)
 

