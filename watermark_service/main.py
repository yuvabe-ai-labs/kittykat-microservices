from fastapi import FastAPI
from routes.image_watermark import router as imager_watermark_router
from routes.text_watermark import router as text_watermark_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imager_watermark_router, tags=["Image WaterMarking"])
app.include_router(text_watermark_router, tags=["Text WaterMarking"])
