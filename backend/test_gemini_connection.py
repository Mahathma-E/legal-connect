import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

api_key = os.environ.get("GEMINI_API_KEY")

print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key prefix: {api_key[:4]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("\nAttempting to generate content...")
    response = model.generate_content("Hello, this is a test connection. Reply with 'Connection Successful'.")
    
    print("\n--- Response ---")
    print(response.text)
    print("----------------")
    print("\nSUCCESS: Gemini API is working correctly.")

except Exception as e:
    print("\nERROR: Failed to connect to Gemini API.")
    print(f"Error details: {e}")
