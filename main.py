from fastapi import FastAPI
import requests
import os

app = FastAPI()

# Ollama API Endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

@app.get("/")
def read_root():
    return {"message": "Ollama is running with Instagram Bot"}

@app.get("/chat")
def chat_with_ai(prompt: str):
    payload = {
        "model": "llama3",
        "prompt": prompt
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
