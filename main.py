from ollama import Client
   client = Client(host='http://localhost:11434')
@app.get("/ask")
def ask(q: str):
    response = client.chat(model='mistral', messages=[
        {"role": "user", "content": q}
    ])
    return {"answer": response['message']['content']}
