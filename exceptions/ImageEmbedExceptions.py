from fastapi import HTTPException, status


class urlNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=200, detail="Image file is required for the search."
        )


class InvalidUrlException(HTTPException):
    def __init__(self, detail="The provided URL is invalid."):
        super().__init__(status_code=200, detail=detail)


class UnauthorizedUrlException(HTTPException):
    def __init__(self, detail="The provided URL is not authenticated or inaccessible."):
        super().__init__(status_code=200, detail=detail)


class ImageProcessingException(HTTPException):
    def __init__(self, detail: str = "Failed to process image from URL."):
        super().__init__(status_code=200, detail=detail)
