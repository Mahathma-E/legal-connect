"""
Enhanced Chatbot Test - User-Friendly Structured Responses
Tests the improved chatbot with various question types
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_enhanced_chatbot():
    print("=" * 80)
    print("Testing Enhanced Constitutional Law Assistant")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Greeting Test",
            "message": "hello",
            "expected_type": "greeting"
        },
        {
            "name": "Direct Article Question",
            "message": "What is Article 21?",
            "expected_type": "structured_answer",
            "should_contain": ["Short Answer", "Constitutional Reference", "Article 21"]
        },
        {
            "name": "Contextual Question (Harsh Words)",
            "message": "if one person talks harsh words to another person",
            "expected_type": "structured_answer",
            "should_contain": ["Article 19", "freedom of speech"]
        },
        {
            "name": "Fundamental Rights Question",
            "message": "Tell me about fundamental rights",
            "expected_type": "structured_answer",
            "should_contain": ["Article", "Fundamental Rights"]
        },
        {
            "name": "Non-Constitutional Question",
            "message": "What is the punishment for theft?",
            "expected_type": "fallback",
            "should_contain": ["not directly covered"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Question: \"{test['message']}\"")
        print(f"Expected: {test['expected_type']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": test['message'], "document": ""},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                
                print(f"\n✓ Status: {response.status_code}")
                print(f"\nResponse:")
                print("-" * 80)
                print(reply)
                print("-" * 80)
                
                # Check expected content
                if 'should_contain' in test:
                    print(f"\nContent Checks:")
                    for expected_text in test['should_contain']:
                        if expected_text.lower() in reply.lower():
                            print(f"  ✅ Contains: '{expected_text}'")
                        else:
                            print(f"  ❌ Missing: '{expected_text}'")
                
                # Check structure
                if test['expected_type'] == 'structured_answer':
                    has_structure = (
                        "Short Answer" in reply or "Constitutional Reference" in reply or
                        "Explanation" in reply or "Conclusion" in reply
                    )
                    if has_structure:
                        print(f"  ✅ Has structured format")
                    else:
                        print(f"  ⚠️  May lack structured format")
                
            else:
                print(f"✗ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout - API call took too long (>30s)")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'='*80}")
    print("Testing Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_chatbot()
