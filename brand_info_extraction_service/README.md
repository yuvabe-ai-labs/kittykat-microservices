# Brand Analysis Service

A Microservice for analyzing brand details from a given URL.

## Table of Contents
- [Definitions of Endpoints](#definitions-of-endpoints)
- [Installation](#installation)
- [Running the Application](#running-the-application)

## Definitions of Endpoints

### 1. POST `/brand/url`

#### Description
This endpoint processes a given brand URL to extract and analyze brand details such as name, category, description, colors, fonts, and logos. It handles invalid URLs gracefully and ensures proper logging for tracking purposes.

---

#### Request Body

- **Attributes:**
  - `url` (string, required): The URL of the brand to analyze.
  - `request_id` (string, optional): A unique identifier for the request, useful for tracking and debugging.

---

#### Responses

##### **200 OK**
A successful response with brand analysis details.

```json
{
  "brand_name": "string",
  "brand_category": ["string", "string"],
  "brand_description": "string",
  "brand_colors": ["string", "string"],
  "brand_fonts": ["string", "string"],
  "brand_logo": ["string", "string"],
}
```

##### **Other than 200 OK**
For all error cases, the response will include empty attributes and a specific error message.

```json
{
  "brand_name": "",
  "brand_category": [],
  "brand_description": "",
  "brand_colors": [],
  "brand_fonts": [],
  "brand_logo": [],
}
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/brand-analysis-service.git
   ```

2. Navigate to the project directory:

   ```bash
   cd brand-analysis-service
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

## Running the Application

To start the FastAPI development server, run the following command:

```bash
uvicorn main:app --reload
```

This will start the server at `http://127.0.0.1:8000/`. You can test the endpoint using tools like [Postman](https://www.postman.com/) or [cURL](https://curl.se/).

---

## Services Used

### 1. **Brand Analysis Utilities**
   - Extracts brand details such as colors, fonts, logos, and descriptions.

### 2. **Selenium Web Scraping**
   - Automates the retrieval of brand-related HTML content.

### 3. **OpenAI API**
   - Processes extracted content to generate structured JSON-like outputs for brand analysis.

---


## Additional Notes

- **Dependencies**: Ensure you have ChromeDriver installed for Selenium to function correctly.
- **Error Handling**: Proper exceptions are raised for invalid URLs, API failures, and scraping issues.
