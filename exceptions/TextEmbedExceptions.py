from fastapi import HTTPException, status


class TextNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Text it required for embeddings")
