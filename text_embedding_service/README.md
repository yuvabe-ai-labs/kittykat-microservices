# text_embedding_service

A Microservice for Backend API Layer for the Kittykat Platform.

## Table of Contents
- [Definitions of Endpoints](#definitions-of-endpoints)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Running the Application](#running-the-application)



## Definitions of Endpoints

### 1.**POST /text/embed**

**Description:**  
Search for similar images using a text query. The endpoint returns embeddings or matching results.

**Request Body:**  
The request must include a JSON object with the following field:
- `search_query` (string, required): The text query to search for.

**Example Request:**  
```json
{
  "text": "example text to search"
}
```

**Response**
- 200 OK: A successful response returns the generated embeddings or search results.
- 400 Bad Request: Returned if the search_query field is missing.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kittykat-ai/platform-services.git
   ```

2. Navigate to the project directory:

   ```bash
   cd platform-services\text_embedding_service
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
   https://storage.cloud.google.com/embedding_model_1/clip_text_model_vitb32.onnx
   ```
   Save the file to the following path in your project:

   ```bash
   text_embedding_service/services/onnx_clip/data/clip_text_model_vitb32.onnx
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

