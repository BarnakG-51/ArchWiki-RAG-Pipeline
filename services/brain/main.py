from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

class BrainService:
    def __init__(self):
        # 1. Connect to local vLLM instance
        # We treat vLLM as an OpenAI-compatible server
        self.llm = OpenAILike(
            api_base="http://llm-engine:8000/v1",
            api_key="fake-key",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            is_chat_model=True,
            timeout=60.0
        )
        
        # 2. Embeddings remain local for lower latency
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        # 3. ChromaDB for Semantic Caching
        self.db = chromadb.PersistentClient(path="./chroma_db")
        self.cache_collection = self.db.get_or_create_collection("semantic_cache")

    def process_query(self, user_query: str, context_chunks: list):
        # Check Semantic Cache first (as implemented in previous step)
        # ... 

        # Construct the RAG prompt
        context_str = "\n".join(context_chunks)
        prompt = f"Arch Wiki Context:\n{context_str}\n\nUser Question: {user_query}"
        
        # vLLM handles the heavy lifting here
        response = self.llm.complete(prompt)
        
        # Update Cache and return
        return str(response)