from fastapi import FastAPI
from routes import imageEmbeded

app = FastAPI()

app.include_router(imageEmbeded.router, tags=["Image-embedding"])
