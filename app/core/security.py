from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional
from app.core.settings import get_settings

settings = get_settings()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def validate_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Validate the API key from the request header.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is missing")
    if api_key != settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


def get_gemini_api_key() -> str:
    """
    Get the Gemini API key from settings.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured")
    return settings.GEMINI_API_KEY
