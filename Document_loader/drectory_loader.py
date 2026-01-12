from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
# from langchain_community.llms import Ollama
# from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import UnstructuredFileLoader

# load_dotenv()
docs=[]
pdf_loader= DirectoryLoader(
    path='Legal document',
    glob='**/*.pdf',
    loader_cls= PyPDFLoader
)

docs.extend(pdf_loader.load())

text_loader= DirectoryLoader(
    path='Legal document',
    glob='**/*.txt',
    loader_cls= TextLoader,
    loader_kwargs={"encoding": "latin-1"} 
)

docs.extend(text_loader.load())

doc_loader= DirectoryLoader(
    path='Legal document',
    glob='**/*.docx',
    loader_cls= Docx2txtLoader,
    silent_errors=True
)


docs.extend(doc_loader.load())

#docs= loader.load()

#print(docs)

print(docs[34].metadata)

