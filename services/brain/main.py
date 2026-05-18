import grpc
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import redis
from redisvl.extensions.llmcache import SemanticCache

# Add project root to Python path so we can import shared modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / ".env")

#Initialise cache
cache = SemanticCache(
    name="arch_wiki_cache",
    redis_url="redis://localhost:6379",
    threshold=0.9 # Only return hits with 90%+ similarity
)

from groq import Groq
import shared.search_pb2 as pb2
import shared.search_pb2_grpc as pb2_grpc

# Initialize Groq client with API key from .env
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class BrainService:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.search_stub = pb2_grpc.SearchServiceStub(self.channel)

    def ask_question(self, question: str):
        request = pb2.SearchRequest(query=question, top_k=10)
        search_results = self.search_stub.Search(request)
        context = "\n---\n".join(search_results.results)

        prompt = f"""
        You are an Arch Linux expert. Use the following wiki context to answer the user.
        If the answer is not in the context, say you don't know.

        CONTEXT:
        {context}

        USER QUESTION: {question}
        """

        message = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast and capable Groq model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return message.choices[0].message.content
    
def get_answer(query):
    brain = BrainService()
    # 1. Check cache first
    cached_response = cache.check(query)
    if cached_response:
        return cached_response
    
    # 2. If no hit, call your existing RAG logic
    response = brain.ask_question(query)
    
    # 3. Store the new answer
    cache.store(query, response)
    return response
    
if __name__ == "__main__":
    print("\033[33mBrain is thinking...\033[0m")
    print(get_answer("How do I install Hyprland?"))
