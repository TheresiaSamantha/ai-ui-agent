# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

class Request(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Task Generator API"}

@app.post("/api/task")
def generate_task(req: Request):
    result = run_agent(req.prompt)
    return {"result": result}
