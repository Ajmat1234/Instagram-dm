from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Ollama AI Bot is running!"}

@app.get("/chat/")
def chat(query: str):
    # Yahan API ka URL daalna hai jo Ollama AI bot se connect kare
    ollama_api_url = "http://localhost:11434/api/generate"
    
    # Ollama API ke liye request payload
    payload = {
        "model": "llama3",
        "prompt": query
    }

    try:
        response = requests.post(ollama_api_url, json=payload)
        response_data = response.json()
        return {"response": response_data.get("response", "No response from AI")}
    
    except Exception as e:
        return {"error": str(e)}
