from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_ollama import OllamaEmbeddings
import os

FILE_PATH = "./docs/"
CHROME_PATH = "./chroma"
def get_embeddings():
    llama = OllamaEmbeddings(model = "llama3.2")
    return llama


def add_docs(chunks):
    database = Chroma(
        persist_directory= CHROME_PATH,
        embedding_function=get_embeddings()
    )
    curritems = database.get(include=[])
    ids_now = set(curritems["file"])
    new = []
    for chunk in chunks:
        if chunk.metadata.get("file") not in ids_now:
            new.append(chunk)
    if new:
        database.add_documents(new)



def load_docs(): 
    loader = DirectoryLoader(
        FILE_PATH, 
        glob="*.pdf",  
        loader_cls=PyPDFLoader  
    )
    documents = loader.load()
    return documents


def get_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, 
        chunk_overlap = 80,
        length_function = len,
        is_separator_regex=False
    )
    return text_splitter.split_documents(docs)


def metadata(chunks): 
    for chunk in chunks:
        full = chunk.metadata.get("source", "unknown.pdf")
        just_name = os.path.basename(full)
        page = str(chunk.metadata.get('page', 'unknown'))
        chunk.metadata['file'] = just_name+page
    return chunks

def gen_vectors():
    docs = load_docs()
    chunks = get_chunks(docs)
    chunks = metadata(chunks)
    add_docs(chunks)




