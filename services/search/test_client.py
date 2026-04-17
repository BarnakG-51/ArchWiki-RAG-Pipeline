import grpc
import shared.search_pb2 as pb2
import shared.search_pb2_grpc as pb2_grpc

def run_test():
    # 1. Open a connection to the server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pb2_grpc.SearchServiceStub(channel)
        
        # 2. Construct a request
        print("🔍 Sending query: 'AUR'")
        request = pb2.SearchRequest(query="Arch User Repository", top_k=3)
        
        # 3. Call the server and get response
        try:
            response = stub.Search(request)
            print(f"✅ Received {len(response.results)} results:")
            for i, result in enumerate(response.results):
                print(f"\nResult {i+1}: {result[:200]}...") # Print first 200 chars
        except grpc.RpcError as e:
            print(f"❌ gRPC Failed: {e.code()} - {e.details()}")

if __name__ == "__main__":
    run_test()