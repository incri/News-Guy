from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not YOUTUBE_API_KEY:
        raise ValueError("Please set YOUTUBE_API_KEY in .env file")
    if not GEMINI_API_KEY:
        raise ValueError("Please set GEMINI_API_KEY in .env file")
