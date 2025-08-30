from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.video_generation_router import router as video_generation_router
from routes.byteplus.router import router as byteplus_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    video_generation_router, tags=["Video Generation"]
)
app.include_router(byteplus_router, tags=["BytePlus Video Generation"])
