# Use the official Tiangolo Uvicorn-Gunicorn image with Python 3.11 slim version
FROM tiangolo/uvicorn-gunicorn:python3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install dependencies for building (e.g., for ChromeDriver)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
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

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb


# Install ChromeDriver
RUN LATEST=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Copy the requirements.txt first to leverage Docker's cache mechanism
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

