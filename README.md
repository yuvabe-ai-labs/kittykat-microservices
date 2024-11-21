# image_embedding_service

A Microservice for Backend API Layer for the Kittykat Platform.

## Table of Contents
- [Definitions of Endpoints](#definitions-of-endpoints)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Running the Application](#running-the-application)



## Definitions of Endpoints

### **1. POST /image/embed/file**

**Description:**  
Generates embeddings for an uploaded image file.

**Request Body:**  
- **Parameter:**  
  - `file` (required): Image file to be embedded.


**Response**
- 200 OK: A successful response returns the generated embeddings 
- 400 : Bad Request: Image file is missing.

### **2. POST /image/embed/url**

**Description:**  
Generates embeddings for an image provided via a URL.

**Request Body:**  
- **Parameter:**  
  - `url` (string,required): URL of the image to be embedded.


**Response**
- 200 OK: A successful response returns the generated embeddings 
- 400: Bad Request: URL is missing.

### **3. POST /image/embed/base64**

**Description:**  
Generates embeddings for an image provided in base64 format.

**Request Body:**  
- **Parameter:**  
  - `ubase64_image` (string,required): base64 encoded string of the image..


**Response**
- 200 OK: A successful response returns the generated embeddings 
- 400: Bad Request: URL is missing.


## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kittykat-ai/platform-services.git
   ```

2. Navigate to the project directory:

   ```bash
   cd platform-services\image_embedding_service
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Linux/Mac
   venv\Scripts\activate       # On Windows
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
5. Download the Model File

   Download the required model file from the following URL:
   ```bash
   https://storage.cloud.google.com/embedding_model_1/clip_image_model_vitb32.onnx
   ```
   Save the file to the following path in your project:

   ```bash
   image_embedding_service/services/onnx_clip/data/clip_image_model_vitb32.onnx
   ```


## Running the Application

To start the FastAPI development server, run the following command:

```bash
fastapi dev
```

OR

```bash
uvicorn main:app --reload
```

