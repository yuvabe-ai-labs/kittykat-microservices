# Use the tiangolo FastAPI image as the base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure wget is available for downloading the model
RUN apt-get update && apt-get install -y wget && apt-get clean

# Create the model directory and download the ONNX model file
RUN mkdir -p /app/services/onnx_clip/data && \
    wget -O /app/services/onnx_clip/data/clip_text_model_vitb32.onnx \
    "https://storage.googleapis.com/embedding_model_1/clip_text_model_vitb32.onnx"

# Set environment variables (optional)
ENV MODEL_PATH="/app/services/onnx_clip/data/clip_text_model_vitb32.onnx"

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Run with Uvicorn multi-worker mode
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
