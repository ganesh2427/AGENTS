import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment variables")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    
    # Test with a simple prompt
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Hello, can you respond with 'API working correctly'?")
    
    print(f"✅ Gemini API Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error testing Gemini API: {str(e)}")