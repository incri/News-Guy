from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    youtube_api_key: str
    gemini_api_key: str

    # Database
    database_url: str = "sqlite:///./news_guy.db"

    # FAISS
    faiss_index_path: str = "data/faiss_index"

    # YouTube Channel
    channel_id: str = "UCsBjURrPoezykLs9EqgamOA"  # Fireship channel ID

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
