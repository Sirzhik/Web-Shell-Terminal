FROM python:3.11-slim

ARG SECRET=blah_blah_blah
ARG ADMIN_PASSWORD=admin
ARG PORT=2280
ARG HOST=0.0.0.0
ARG DB_HOST=0.0.0.0
ARG DB_TYPE=sqlite
ARG DB_USER=user
ARG DB_PASSWORD=password
ARG DB_NAME=dbname
ARG DB_DIRECTORY=database
ARG DB_PORT=5432

ENV DB_HOST=${DB_HOST} \
    DB_TYPE=${DB_TYPE} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_NAME=${DB_NAME} \
    DB_PORT=${DB_PORT} \
    SECRET=${SECRET} \
    ADMIN_PASSWORD=${ADMIN_PASSWORD} \
    PORT=${PORT} \
    HOST=${HOST}

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    npm \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python3 -c "import fastapi; print('FastAPI installed successfully')"

COPY src/ src/

WORKDIR /app/src
RUN npm install @xterm/xterm 

EXPOSE ${DB_PORT}
CMD ["python3", "main.py"]
