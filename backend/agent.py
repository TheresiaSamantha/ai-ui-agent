# backend/agent.py
import os
from dotenv import load_dotenv

from mcp_server import list_files, read_file
from google import genai
from google.genai import types

load_dotenv()  # Load .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_agent(user_prompt: str):
    # Step 1: AI lihat file apa yang tersedia
    available = list_files()
    # → ['login_context.json', 'login_context.md', 'login.json', 'login.xml']

    # Step 2: AI memilih file yang relevan dengan prompt
    # (Gemini memutuskan sendiri file mana yang dipakai)
    selection_prompt = f"""
    File tersedia: {available}
    Pertanyaan user: "{user_prompt}"
    File mana yang paling relevan? Jawab HANYA dengan nama file.
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=selection_prompt
    )
    chosen_file = response.text.strip()

    # Step 3: Baca file yang dipilih AI
    file_content = read_file(chosen_file)

    # Step 4: Generate instruksi berdasarkan konten file
    final_prompt = f"""
    Konten UI dari {chosen_file}:
    {file_content}

    Tugas user: {user_prompt}
    Hasilkan 7 langkah instruksi dalam format JSON.
    """
    result = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=final_prompt
    )
    return result.text
