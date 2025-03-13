from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.moodboard_prompt_generator import (
    router as moodboard_prompt_generator_router,
)
from routes.prompt_enhancer import router as prompt_enhancer_router
from routes.json_convertor import router as json_convertor_router

from routes.image_to_description import router as image_to_description_router


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

app.include_router(prompt_enhancer_router, tags=["Prompt Enhance"])
app.include_router(json_convertor_router, tags=["JSON Convertor"])

app.include_router(image_to_description_router, tags=["Image to Description"])

