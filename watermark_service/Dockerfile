FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--config", "gunicorn.conf.py"]
