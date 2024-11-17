from fastapi import FastAPI
from endpoints import imageEmbeded

app = FastAPI()

app.include_router(imageEmbeded.router, tags=["Image-embedding"])
