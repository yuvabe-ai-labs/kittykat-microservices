from fastapi import FastAPI
from routes.boards import router as boards_router
from routes.pins import router as pins_router
from routes.media import router as media_router
from routes.user_accounts import router as user_accounts_router
from routes.ad_accounts import router as ad_accounts_router
from routes.campaigns import router as campaigns_router
from routes.feeds import router as feeds_router

app = FastAPI()

# Include the Boards router
app.include_router(boards_router, tags=["Boards"])

# Include the Pins router
app.include_router(pins_router, tags=["Pins"])

# Include the Media router
app.include_router(media_router, tags=["Media"])

# Include the User Accounts router
app.include_router(user_accounts_router, tags=["User Accounts"])

# Include the Ad Accounts router
app.include_router(ad_accounts_router, tags=["AD Accounts"])

# Include the Campaigns router
app.include_router(campaigns_router,tags=["Campaigns"])

# Include the Feeds router
app.include_router(feeds_router,tags=["Feeds"])


