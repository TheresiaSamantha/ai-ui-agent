# backend/agent.py
import os
import json
import uuid
from dotenv import load_dotenv

from mcp_server import list_files, read_file
from google import genai
from google.genai import types

load_dotenv()  # Load .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# System prompt with Chain-of-Thought and Few-Shot examples
SYSTEM_PROMPT = """You are an AI assistant that generates structured task instructions for UI navigation and interaction.

Your role is to analyze UI context and user requests, then output detailed step-by-step instructions in a strict JSON format.

THINK STEP-BY-STEP:
1. Understand the user's goal
2. Analyze the UI structure provided
3. Break down the task into exactly 7 logical steps
4. Each step must have a clear action type and expected outcome

OUTPUT FORMAT (JSON ONLY, NO MARKDOWN, NO EXPLANATION):
{
  "task_id": "unique-uuid",
  "title": "Clear task title",
  "source_file": "filename.json",
  "total_steps": 7,
  "steps": [
    {
      "step_number": 1,
      "action": "NAVIGATE|LOCATE|CLICK|INPUT|SUBMIT|VERIFY|COMPLETE",
      "description": "Clear description of what to do",
      "ui_element": "CSS selector or null",
      "expected_result": "What should happen after this step"
    }
  ]
}

ACTION TYPES:
- NAVIGATE: Open URL or navigate to page
- LOCATE: Find and identify UI element
- CLICK: Click button or link
- INPUT: Enter text into field
- SUBMIT: Submit form
- VERIFY: Check result or condition
- COMPLETE: Final confirmation

EXAMPLE 1:
User: "How do I login?"
UI Context: Login form with username, password, and submit button

Output:
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Login to Application",
  "source_file": "login_context.json",
  "total_steps": 7,
  "steps": [
    {
      "step_number": 1,
      "action": "NAVIGATE",
      "description": "Open the application login page",
      "ui_element": null,
      "expected_result": "Login page is displayed"
    },
    {
      "step_number": 2,
      "action": "LOCATE",
      "description": "Find the username input field",
      "ui_element": "input#user-name",
      "expected_result": "Username field is visible and accessible"
    },
    {
      "step_number": 3,
      "action": "INPUT",
      "description": "Enter valid username",
      "ui_element": "input#user-name",
      "expected_result": "Username is entered in the field"
    },
    {
      "step_number": 4,
      "action": "LOCATE",
      "description": "Find the password input field",
      "ui_element": "input#password",
      "expected_result": "Password field is visible and accessible"
    },
    {
      "step_number": 5,
      "action": "INPUT",
      "description": "Enter valid password",
      "ui_element": "input#password",
      "expected_result": "Password is entered in the field"
    },
    {
      "step_number": 6,
      "action": "SUBMIT",
      "description": "Click the login button to submit credentials",
      "ui_element": "input#login-button",
      "expected_result": "Login form is submitted"
    },
    {
      "step_number": 7,
      "action": "VERIFY",
      "description": "Confirm successful login and dashboard display",
      "ui_element": null,
      "expected_result": "User is successfully logged in and redirected to dashboard"
    }
  ]
}

IMPORTANT: 
- Always output valid JSON only
- No markdown code blocks (```json)
- No explanatory text before or after
- Exactly 7 steps
- Use realistic UI selectors based on context
"""

def run_agent(user_prompt: str):
    """
    Original simple agent function (kept for backwards compatibility)
    """
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

def run_agent_structured(user_prompt: str, selected_file: str = None):
    """
    Enhanced agent with structured JSON output
    
    Args:
        user_prompt: User's task request (e.g., "How do I login?")
        selected_file: Optional specific file to use, otherwise AI selects
    
    Returns:
        dict: Structured task instructions in JSON format
    """
    try:
        # Step 1: Get available files
        available_files = list_files()
        
        # Step 2: Select file (use provided or let AI choose)
        if selected_file and selected_file in available_files:
            chosen_file = selected_file
        else:
            # Let AI choose the most relevant file
            selection_prompt = f"""Available UI context files: {available_files}
            
User request: "{user_prompt}"

Select the MOST RELEVANT file for this task. Respond with ONLY the filename, nothing else."""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=selection_prompt
            )
            chosen_file = response.text.strip().strip('"').strip("'")
            
            # Validate chosen file
            if chosen_file not in available_files:
                chosen_file = available_files[0]  # Fallback to first file
        
        # Step 3: Read the selected file
        file_content = read_file(chosen_file)
        
        # Step 4: Generate structured instructions
        task_prompt = f"""{SYSTEM_PROMPT}

NOW GENERATE INSTRUCTIONS FOR THIS TASK:

UI Context File: {chosen_file}
UI Content: {json.dumps(file_content) if isinstance(file_content, dict) else file_content[:2000]}

User Request: "{user_prompt}"

Remember: Output ONLY valid JSON matching the schema. No markdown, no explanation."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=task_prompt
        )
        
        # Parse response
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        # Parse JSON
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback: create structured response manually
            result = {
                "task_id": str(uuid.uuid4()),
                "title": f"Task: {user_prompt}",
                "source_file": chosen_file,
                "total_steps": 7,
                "steps": [
                    {
                        "step_number": i+1,
                        "action": "COMPLETE",
                        "description": f"Step {i+1} for: {user_prompt}",
                        "ui_element": None,
                        "expected_result": "Step completed"
                    }
                    for i in range(7)
                ]
            }
        
        # Ensure required fields
        if "task_id" not in result:
            result["task_id"] = str(uuid.uuid4())
        if "source_file" not in result:
            result["source_file"] = chosen_file
        if "total_steps" not in result:
            result["total_steps"] = len(result.get("steps", []))
        
        return result
    
    except Exception as e:
        # Error fallback
        return {
            "task_id": str(uuid.uuid4()),
            "title": f"Error: {str(e)}",
            "source_file": "error",
            "total_steps": 1,
            "steps": [
                {
                    "step_number": 1,
                    "action": "COMPLETE",
                    "description": f"Error occurred: {str(e)}",
                    "ui_element": None,
                    "expected_result": "Please try again"
                }
            ]
        }

# Test function
if __name__ == "__main__":
    print("Testing AI Agent...")
    result = run_agent_structured("How do I login?")
    print(json.dumps(result, indent=2))
