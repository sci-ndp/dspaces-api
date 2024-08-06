from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    swagger_title: str = "EcoExplorer API"
    swagger_description: str = "API documentation"
    swagger_version: str = "0.0.1"

    model_config = {
        "env_file": "./env_variables/.env_swagger",
        "extra": "allow",
    }

swagger_settings = Settings()
