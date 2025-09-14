from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.byteplus.router import router as byteplus_router
from routes.replicate.router import router as replicate_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(replicate_router, tags=["Replicate Video Generation"])
app.include_router(byteplus_router, tags=["BytePlus Video Generation"])
