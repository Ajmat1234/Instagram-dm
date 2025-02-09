FROM docker.io/ollama/ollama:latest

# Dependencies install करें
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install fastapi uvicorn requests python-ollama

# start.sh और main.py copy करें
COPY start.sh main.py /app/
WORKDIR /app

# Script को executable बनाएं
RUN chmod +x start.sh

# Port expose करें
EXPOSE 8000 11434

# Entrypoint set करें
CMD ["./start.sh"]
