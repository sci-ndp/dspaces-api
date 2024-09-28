from pydantic_settings import BaseSettings


class SwaggerSettings(BaseSettings):
    swagger_title: str = "DXSpaces API"
    swagger_description: str = "RESTful API for DataSpaces"
    swagger_version: str = "0.0.1"

    model_config = {
        "env_file": "./env_variables/.env_swagger",
        "extra": "allow",
    }

settings = SwaggerSettings()