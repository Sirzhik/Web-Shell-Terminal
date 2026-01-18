FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python3 -c "import fastapi; print('FastAPI installed successfully')"

COPY src/ src/

RUN npm install @xterm/xterm --prefix src/static
WORKDIR /app/src

EXPOSE 2280

CMD ["python3", "main.py"]
