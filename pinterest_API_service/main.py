from fastapi import FastAPI
from routes.boards import router as boards_router
from routes.pins import router as pins_router

app = FastAPI()

# Include the Boards router
app.include_router(boards_router, tags=["Boards"])

# Include the Pins router
app.include_router(pins_router, tags=["Pins"])

