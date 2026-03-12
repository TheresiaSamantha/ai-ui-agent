# backend/main.py
import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from mcp_server import list_files, read_file
from agent import run_agent_structured

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI UI Agent API",
    description="Backend API for AI-powered UI task instruction generation",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TaskRequest(BaseModel):
    prompt: str
    file: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    title: str
    source_file: str
    total_steps: int
    steps: List[Dict[str, Any]]

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI UI Agent API is running",
        "endpoints": {
            "files": "/api/files",
            "task": "/api/task",
            "websocket": "/ws/task-stream"
        }
    }

@app.get("/api/files")
async def get_files():
    """Get list of available UI context files from Data_Analis folder"""
    try:
        files = list_files()
        return {
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.post("/api/task")
def generate_task(req: TaskRequest):
    """
    Generate structured task instructions using AI Agent
    This is a REST API fallback when WebSocket is not available
    """
    try:
        # Validate input
        if not req.prompt or not req.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Run the AI agent
        result = run_agent_structured(req.prompt, req.file)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating task: {str(e)}")

@app.websocket("/ws/task-stream")
async def websocket_task_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming AI reasoning and task generation
    Provides real-time step-by-step updates to the frontend
    """
    await websocket.accept()
    
    try:
        # Receive task request from client
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        prompt = request_data.get("prompt", "")
        selected_file = request_data.get("file")
        
        if not prompt.strip():
            await websocket.send_json({
                "error": "Prompt cannot be empty",
                "done": True
            })
            await websocket.close()
            return
        
        # Send thinking status
        await websocket.send_json({
            "status": "thinking",
            "message": "AI is analyzing your request..."
        })
        
        # Run agent in thread to avoid blocking
        result = await asyncio.to_thread(
            run_agent_structured,
            prompt,
            selected_file
        )
        
        # Send task title
        await websocket.send_json({
            "title": result.get("title", "Task Instructions"),
            "source_file": result.get("source_file", ""),
            "total_steps": result.get("total_steps", 7)
        })
        
        # Stream each step with a small delay for visual effect
        steps = result.get("steps", [])
        for step in steps:
            await asyncio.sleep(0.3)  # Small delay for better UX
            await websocket.send_json({
                "step": step,
                "done": False
            })
        
        # Send completion signal
        await websocket.send_json({
            "done": True,
            "message": "Task generation complete"
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except json.JSONDecodeError:
        await websocket.send_json({
            "error": "Invalid JSON format",
            "done": True
        })
    except Exception as e:
        await websocket.send_json({
            "error": f"Server error: {str(e)}",
            "done": True
        })
    finally:
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting AI UI Agent API Server")
    print("=" * 60)
    print("📡 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/task-stream")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
