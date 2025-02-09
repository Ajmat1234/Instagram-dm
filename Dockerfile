# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# Python aur packages install karein
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install fastapi uvicorn requests

# Environment variable set karein
ENV PORT=8000

# Port expose karein
EXPOSE $PORT

# CMD ko update karein (main.py ke liye)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
