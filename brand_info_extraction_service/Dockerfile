FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

WORKDIR /app

COPY . .


# Install necessary dependencies, including FastAPI and other required packages
RUN pip install --no-cache-dir -r requirements.txt

# Install wget to ensure it's available for downloading any resources
RUN apt-get update && apt-get install -y wget && apt-get clean

# Set the OpenAI API key as an environment variable
ENV OPENAI_API_KEY="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"


# Ensure wget is available for downloading the model
RUN apt-get update && apt-get install -y wget




