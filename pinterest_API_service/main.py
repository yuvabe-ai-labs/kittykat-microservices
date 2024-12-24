from fastapi import FastAPI
from routes.boards import router as boards_router
from routes.pins import router as pins_router
from routes.media import router as media_router
from routes.user_accounts import router as user_accounts_router

app = FastAPI()

# Include the Boards router
app.include_router(boards_router, tags=["Boards"])

# Include the Pins router
app.include_router(pins_router, tags=["Pins"])

# Include the Media router
app.include_router(media_router, tags=["Media"])

# Include the Media router
app.include_router(user_accounts_router, tags=["User Accounts"])


