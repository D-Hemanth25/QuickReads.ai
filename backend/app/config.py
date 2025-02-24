from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    session_secret_key: str
    redis_url: str
    gemini_api_key: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
