import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Model yang tersedia:")
try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
except Exception as e:
    print(f"Error: {e}")
