from fastapi import HTTPException, Header


async def verify_api_token(authorization: str = Header(...)):
    """Verify that the API token is provided."""
    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing API token")
    return token
