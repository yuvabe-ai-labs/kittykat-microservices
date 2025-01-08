FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

WORKDIR /app

EXPOSE 8000

COPY . .

# Install necessary dependencies, including FastAPI and other required packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn" ,"main:app" ,"--host", "0.0.0.0" ,"--port" ,"8000"]





