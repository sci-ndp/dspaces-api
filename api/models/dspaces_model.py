import json

from pydantic import BaseModel, Field, model_validator


class Interval(BaseModel):
    start: int = Field(title="the lower bound of a range", ge=-1)
    span: int = Field(title="the size of a range", ge=0)

class BoundingBox(BaseModel):
    bounds: list[Interval]

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class DSObject(BaseModel):
    name: str
    namespace: str = None
    version: int
    bounds: list[Interval]

class RequestList(BaseModel):
    requests: list[DSObject] = []

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
class DSRegHandle(BaseModel):
    namespace: str
    parameters: dict

class CSVIngestionRequest(BaseModel):
    namespace: str = Field(title="Namespace", description="The namespace to store the CSV data under")
    version: int = Field(default=0, title="Version", description="Version number for the stored objects", ge=0)
    chunk_size: int = Field(default=10000, title="Chunk Size", description="Number of rows to process at once", gt=0)

class CSVIngestionResponse(BaseModel):
    file_path: str
    total_rows: int
    total_columns: int
    columns: list[str]
    namespace: str
    version: int
    stored_objects: dict
    success: bool
    message: str