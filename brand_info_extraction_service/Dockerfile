# Use the official Tiangolo Uvicorn-Gunicorn image with Python 3.11 slim version
FROM tiangolo/uvicorn-gunicorn:python3.11-slim

# Set the working directory to /app
WORKDIR /app

EXPOSE 8001

# Install Playwright dependencies and Playwright itself
RUN pip install --no-cache-dir playwright \
    && playwright install

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    libx11-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgbm-dev \
    libasound2 \
    libappindicator3-1 \
    libcurl4 \
    libxrandr2 \
    libxss1 \
    lsb-release \
    fonts-liberation \
    libvulkan1 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*



# Copy the requirements.txt first to leverage Docker's cache mechanism
COPY requirements.txt .

# Install the rest of the dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

CMD ["uvicorn" ,"main:app" ,"--reload" ,"--host", "0.0.0.0" ,"--port" ,"8001"]