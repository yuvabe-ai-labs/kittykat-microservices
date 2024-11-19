FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install necessary dependencies, including FastAPI and other required packages
RUN pip install --no-cache-dir -r requirements.txt

# Ensure wget is available for downloading the model
RUN apt-get update && apt-get install -y wget

# Download the ONNX model file directly and save it in the desired path
RUN mkdir -p /app/services/onnx_clip/data && \
    wget -O /app/services/onnx_clip/data/clip_text_model_vitb32.onnx "https://storage.cloud.google.com/embedding_model_1/clip_text_model_vitb32.onnx/clip_text_model_vitb32.onnx"

# Copy the FastAPI app code into the container
COPY . .

# Set environment variables (optional, for code references)
ENV MODEL_PATH="/app/services/onnx_clip/data/clip_text_model_vitb32.onnx"

# Expose port 8000 for FastAPI
EXPOSE 8000

# Use FastAPI's development server to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
