from fastapi import FastAPI
from ollama import Client  # Correct import

# Ollama client ko port ke saath initialize karein
client = Client(host='http://localhost:11434')  # Ollama default port

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Ollama AI Running!"}

@app.get("/ask")
def ask_ai(q: str):
    try:
        response = client.chat(model="mistral", messages=[{"role": "user", "content": q}])
        return {"response": response['message']['content']}
    except Exception as e:
        return {"error": str(e)}
