from fastapi import FastAPI
from endpoints import text_embedded

app = FastAPI()


app.include_router(text_embedded.router, tags=["Text-embedded microservice"])
