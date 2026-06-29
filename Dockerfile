FROM tiangolo/uvicorn-gunicorn:python3.11-slim

ENV PORT=7860

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .