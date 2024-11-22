from fastapi import HTTPException, status


class urlNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Image file is required for the search."
        )
