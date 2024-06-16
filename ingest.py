from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader 
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os

DATA_PATH = "data/"
DB_FAISS_PATH = "vectorstores/db_faiss"

def create_vector_db():
    print("Loading documents from", DATA_PATH)
    loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    print("Splitting documents into chunks")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks")

    print("Creating embeddings for the documents")
    embeddings = HuggingFaceEmbeddings(model_name='hkunlp/instructor-xl', model_kwargs={'device': 'cpu'})
    db = FAISS.from_documents(texts, embeddings)
    
    if not os.path.exists(DB_FAISS_PATH):
        os.makedirs(DB_FAISS_PATH)
    
    print(f"Saving the FAISS vector store to {DB_FAISS_PATH}")
    db.save_local(DB_FAISS_PATH)
    print("FAISS vector store creation completed successfully")

if __name__ == "__main__":
    create_vector_db()
