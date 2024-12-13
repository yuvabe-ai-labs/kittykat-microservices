from fastapi import FastAPI
from routes import brand_analysis
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()  


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, but you can restrict this
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include video processing routes
app.include_router(brand_analysis.router,tags=["Brand Data"])
