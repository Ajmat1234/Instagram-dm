from fastapi import FastAPI
from ollama import Client

app = FastAPI()
client = Client(host='http://localhost:11434')  # Direct local connection

@app.get("/ask")
def ask(q: str):
    response = client.chat(model='mistral', messages=[
        {"role": "user", "content": q}
    ])
    return {"answer": response['message']['content']}
