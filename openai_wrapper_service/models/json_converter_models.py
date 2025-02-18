from pydantic import BaseModel
from typing import Optional, List, Union


class JsonConverterRequest(BaseModel):
    data: str  # The raw input data to be converted into JSON
    fields: List[str]  # List of field names for JSON mapping
    type: str  # Either "Single Object" or "List of Objects"


class JsonConverterResponse(BaseModel):
    converted_json: Union[dict, List[dict]]  # Resulting JSON data
