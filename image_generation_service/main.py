from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.replicate_image_generator import router as replicate_image_generator_router
from routes.falai_image_generator import router as falai_image_generator_router
from routes.fashnai_image_generator import router as fashn_image_generator_router
from routes.replicate_model_trainer import router as replicate_model_trainer_router

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

app.include_router(falai_image_generator_router, tags=["FalAi Image Generator"])
app.include_router(fashn_image_generator_router, tags=["Fashn Ai Image Generator"])
app.include_router(replicate_model_trainer_router, tags=["Replicate Model Trainer"])
