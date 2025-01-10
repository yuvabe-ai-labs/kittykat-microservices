from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.replicate_image_generator import router as replicate_image_generator_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    replicate_image_generator_router, tags=["Replicate Image Generation"]
)
