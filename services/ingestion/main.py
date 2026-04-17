from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import requests
from bs4 import BeautifulSoup
import os

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

def scrape_arch_wiki(page_name):
    url = f"https://wiki.archlinux.org/title/{page_name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch {page_name}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # The Arch Wiki stores the main content in a div with id 'mw-content-text'
    content = soup.find('div', {'id': 'mw-content-text'})
    
    # Remove unwanted elements like the table of contents and edit buttons
    for div in content.find_all(['div', 'table'], {'class': ['toc', 'archwiki-template-meta']}):
        div.decompose()

    # Save as Markdown-friendly text
    file_path = f"data/raw/{page_name.replace('/', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {url}\n\n")
        f.write(content.get_text(separator='\n'))
        
    print(f"✅ Saved {page_name} to {file_path}")

def ingest_docs():
    '''
    Read documents in the /data/raw folder and import them in the pipeline
    '''
    
    documents = SimpleDirectoryReader('./data/raw').load_data()

    db = chromadb.PersistentClient(path="./chromadb")
    chroma_collection = db.get_or_create_collection("arch-wiki")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context = storage_context,
        show_progress=True
    )

    print(f"[INGESTION] Successfully Ingested {len(documents)} documents!")

if __name__ == "__main__":
    # Test with a few essential pages
    pages = ["Installation_guide", "Hyprland", "Arch_User_Repository"]
    for page in pages:
        scrape_arch_wiki(page)
    ingest_docs()