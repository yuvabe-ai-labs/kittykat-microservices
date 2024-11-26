from fastapi import FastAPI
from routes.imageEmbeded import router as ImageEmbedRouter
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)

# Include the router for image embedding
app.include_router(ImageEmbedRouter, tags=["Image-embedding"])


# Log application startup
@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up........")


# Log application shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down.......")
