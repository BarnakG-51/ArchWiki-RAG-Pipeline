from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

def ingest_docs():
    documents = SimpleDirectoryReader('./data/raw').load_data()

    db = chromadb.PersistentClient(path="./chromadb")
    chroma_collection = db.get_or_create_collection("arch-wiki")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print(f"[INGESTION] Successfully Ingested {len(documents)} documents!")

if __name__ == "__main__":
    ingest_docs()