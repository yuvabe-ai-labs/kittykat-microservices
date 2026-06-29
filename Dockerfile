FROM tiangolo/uvicorn-gunicorn:python3.11-slim


# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to install dependencies
COPY requirements.txt .

# Install necessary dependencies (FastAPI, ONNX Runtime, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Ensure wget and required dependencies are available
RUN apt-get update && apt-get install -y wget && apt-get clean

# Download the ONNX model file and save it in the desired path
RUN mkdir -p /app/services/onnx_clip/data && \
    wget -O /app/services/onnx_clip/data/clip_image_model_vitb32.onnx \
    "https://storage.cloud.google.com/embedding_model_1/clip_image_model_vitb32.onnx"

# Copy the FastAPI app code into the container
COPY . .

# Set the model path as an environment variable (for reference in your code)
ENV MODEL_PATH="/app/services/onnx_clip/data/clip_image_model_vitb32.onnx"

# Expose port 8000 to access the FastAPI app
EXPOSE 7860

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
