from fastapi import FastAPI
import ollama

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Ollama AI Running!"}

@app.get("/ask")
def ask_ai(q: str):
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": q}])
    return {"response": response["message"]["content"]}
