import grpc
from concurrent import futures
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import MockLLM
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = MockLLM()

import shared.search_pb2 as pb2
import shared.search_pb2_grpc as pb2_grpc


class searchServicer:
    def __init__(self):
        self.db = chromadb.PersistentClient(path="./chromadb")
        self.chromaCollection = self.db.get_collection("arch-wiki")
        self.vectorStore = ChromaVectorStore(chroma_collection=self.chromaCollection)
        self.index = VectorStoreIndex.from_vector_store(self.vectorStore)
        self.queryEngine = self.index.as_query_engine(similarity_top_k=3)
        self.index = VectorStoreIndex.from_vector_store(
            self.vectorStore, 
            embed_model=Settings.embed_model # Explicitly pass it here
        )   

    def search(self, request, context):
        # In your Search method, try retrieving everything to verify data exists
        response = self.queryEngine.query(request.query)
        results = [node.get_content() for node in response.source_nodes]
        return pb2.SearchResponse(results=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_SearchServiceServicer_to_server(searchServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("\033[32mSearch Service started at port 50051\033[0m")
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    serve()