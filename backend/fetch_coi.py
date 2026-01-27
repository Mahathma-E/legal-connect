import requests
import json
import os

# url = "https://raw.githubusercontent.com/Yash-Handa/The_Constitution_Of_India/master/COI.json"
url = "https://raw.githubusercontent.com/civictech-India/constitution-of-india/master/constitution_of_india.json"
save_path = "civic_tech_coi.json"

def fetch_and_inspect():
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print("Download complete.")
        
        # Inspection
        print(f"Top level structure type: {type(data)}")
        if isinstance(data, list):
            print(f"List length: {len(data)}")
            
            # The summary said index 0 is Articles
            if len(data) > 0:
                articles = data[0]
                print(f"Articles type: {type(articles)}")
                if isinstance(articles, list):
                    print(f"Number of articles: {len(articles)}")
                    
                    # Print first article to see keys
                    if len(articles) > 0:
                        first = articles[0]
                        print("\nSample Article Structure:")
                        print(json.dumps(first, indent=2))
                        
                        # Check specific key for text
                        # Keys might be "Name", "ArtDesc", "Content", etc.
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_inspect()
