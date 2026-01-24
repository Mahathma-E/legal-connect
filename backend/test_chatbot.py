"""
Test script for Legal Assistant Chatbot
Tests greeting handling and constitutional question responses
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_chatbot():
    print("=" * 70)
    print("Testing Legal Assistant Chatbot")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Greeting Test - 'hi'",
            "message": "hi",
            "expected": "greeting response"
        },
        {
            "name": "Greeting Test - 'hello'",
            "message": "hello",
            "expected": "greeting response"
        },
        {
            "name": "Greeting Test - 'good morning'",
            "message": "good morning",
            "expected": "greeting response"
        },
        {
            "name": "Constitutional Question - Article 21",
            "message": "What is Article 21?",
            "expected": "constitutional answer"
        },
        {
            "name": "Constitutional Question - Fundamental Rights",
            "message": "Tell me about fundamental rights",
            "expected": "constitutional answer"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Message: \"{test['message']}\"")
        print(f"   Expected: {test['expected']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": test['message'], "document": ""},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                
                # Check if it's a greeting response
                is_greeting = "Constitutional Law Assistant" in reply or "👋" in reply
                
                print(f"   ✓ Status: {response.status_code}")
                print(f"   Response Type: {'Greeting' if is_greeting else 'Constitutional Answer'}")
                print(f"   Reply Preview: {reply[:150]}...")
                
                if test['expected'] == 'greeting response' and is_greeting:
                    print(f"   ✅ PASS - Greeting handled correctly")
                elif test['expected'] == 'constitutional answer' and not is_greeting:
                    print(f"   ✅ PASS - Constitutional question processed")
                else:
                    print(f"   ⚠️  WARNING - Response type mismatch")
            else:
                print(f"   ✗ Error: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_chatbot()
