from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.replicate_image_generator import router as replicate_image_generator_router

from routes.falai_image_generator import router as falai_image_generator_router
from routes.fashnai_image_generator import router as fashn_image_generator_router
from routes.replicate_model_trainer import router as replicate_model_trainer_router
from routes.replicate.replicate_models.router import router as replicate_models_router
from routes.replicate.predictions.router import router as replicate_predictions_router

from routes.replicate.router import router as replicate_router
from routes.openai.router import router as openai_router
from routes.magnific.router import router as magnific_router
from routes.byteplus.router import router as byteplus_router
from routes.gemini.router import router as gemini_router

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

app.include_router(falai_image_generator_router,
                   tags=["FalAi Image Generator"])
app.include_router(fashn_image_generator_router,
                   tags=["Fashn Ai Image Generator"])
app.include_router(replicate_model_trainer_router,
                   tags=["Replicate Model Trainer"])
app.include_router(replicate_models_router, tags=["Replicate Models"])
app.include_router(replicate_predictions_router,
                   tags=["Replicate Predictions"])

app.include_router(replicate_router, tags=["Replicate Image Generation"])
app.include_router(openai_router, tags=["OpenAI Image Generation"])
app.include_router(magnific_router, tags=["Magnific Image Upscaling"])
app.include_router(byteplus_router, tags=["BytePlus Image Generation"])
app.include_router(gemini_router, tags=["Gemini Image Generation"])
