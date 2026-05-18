from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.redis import RedisVectorStore
from llama_index.vector_stores.redis.base import IndexSchema
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import redis
import requests
from bs4 import BeautifulSoup
import os

import time

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")

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

# ...existing code...

def ingest_docs():
    '''
    Read documents in the /data/raw folder and import them in the pipeline
    '''

    index_name = f"arch_{int(time.time() * 1000)}"
    
    # Connect to Redis and drop existing index if it exists
    client = redis.from_url("redis://localhost:6380")
    try:
        client.ft(index_name).dropindex()
        print(f"[INFO] Dropped existing index: {index_name}")
    except Exception as e:
        print(f"[INFO] No existing index to drop or error: {e}")
    
    documents = SimpleDirectoryReader('./data/raw').load_data()
    
    # Get the actual embedding dimension from the model
    test_embedding = Settings.embed_model.get_text_embedding("test")
    embedding_dim = len(test_embedding)
    print(f"[INFO] Using embedding dimension: {embedding_dim}")
    
    # Use standard IndexSchema constructor with all fields
    index_schema = IndexSchema(
        name=index_name,
        prefix=index_name,  # Make prefix unique to avoid conflicts
        vector_dim=embedding_dim,
        distance_metric="COSINE",
        text_field="content",
        embedding_field="embedding",
        index_type="FLAT",  # Add required field
        algorithm="HNSW"    # Add required field
    )
    
    vector_store = RedisVectorStore(
        index_schema=index_schema,
        redis_url="redis://localhost:6380"
    )
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    
    print(f"[INGESTION] Successfully Ingested {len(documents)} documents!")

# ...existing code...

if __name__ == "__main__":
    # Test with a few essential pages
    pages = ["Installation_guide", "Hyprland", "Arch_User_Repository", "Frequently_Asked_Questions"]
    # for page in pages:
    #     scrape_arch_wiki(page)
    ingest_docs()