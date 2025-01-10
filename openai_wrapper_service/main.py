from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.moodboard_prompt_generator import (
    router as moodboard_prompt_generator_router,
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    moodboard_prompt_generator_router, tags=["MoodBoard Prompt Generation"]
)
