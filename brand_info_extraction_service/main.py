from fastapi import FastAPI
from routes.brand_data import router as brand_data_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include the brand data router
app.include_router(brand_data_router, tags=["Brand Data"])
