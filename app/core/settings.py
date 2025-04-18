from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # API Keys
    YOUTUBE_API_KEY: str
    GEMINI_API_KEY: str

    # Application Settings
    APP_NAME: str = "News Guy"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Storage Settings
    STORAGE_DIR: Path = Path("storage")
    INDEX_PATH: Path = STORAGE_DIR / "captions.index"
    METADATA_PATH: Path = STORAGE_DIR / "metadata.json"
    LATEST_VIDEO_PATH: Path = STORAGE_DIR / "latest_video.json"

    # Model Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"

    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = 5
    CHUNK_SIZE: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
