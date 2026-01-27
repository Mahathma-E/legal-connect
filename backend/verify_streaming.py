import requests
import json
import time

def test_streaming():
    url = "http://localhost:5000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": "Explain Article 21 briefly."}
    
    print("Sending request...")
    start_time = time.time()
    
    # Use stream=True to handle streaming response
    with requests.post(url, json=data, headers=headers, stream=True) as response:
        print(f"Response status: {response.status_code}")
        
        chunk_count = 0
        first_chunk_time = None
        
        if response.status_code == 200:
            print("Receiving chunks:")
            for chunk in response.iter_content(chunk_size=None): # Auto chunk size
                if chunk:
                    if chunk_count == 0:
                        first_chunk_time = time.time()
                        print(f"First chunk received after {first_chunk_time - start_time:.2f}s")
                    
                    chunk_count += 1
                    # Decode and print a preview of the chunk
                    text = chunk.decode('utf-8')
                    print(f"Chunk {chunk_count}: {len(text)} bytes - {text[:30]}...")
            
            print(f"\nTotal chunks: {chunk_count}")
            if chunk_count > 1:
                print("SUCCESS: Response was streamed.")
            else:
                print("WARNING: Response came in a single chunk (might be too short or not streaming).")
        else:
            print("Failed to connect.")

if __name__ == "__main__":
    try:
        test_streaming()
    except Exception as e:
        print(f"Error: {e}")
