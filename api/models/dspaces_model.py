from pydantic import BaseModel, Field, model_validator
import json

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