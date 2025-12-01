from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Transport Manager"
    SECRET_KEY: str = "supersecretkey"
    DEBUG: bool = True

settings = Settings()
