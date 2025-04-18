from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class CaptionItem(BaseModel):
    text: str = Field(..., description="The caption text")
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")


class VideoInfo(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    published_at: datetime = Field(..., description="Publication date")
    channel_id: str = Field(..., description="YouTube channel ID")


class CaptionResponse(BaseModel):
    captions: List[CaptionItem] = Field(..., description="List of caption items")
    video_info: VideoInfo = Field(..., description="Video information")


class SearchResult(BaseModel):
    text: str = Field(..., description="Matching text segment")
    video_id: str = Field(..., description="YouTube video ID")
    timestamp: float = Field(..., description="Timestamp in seconds")
    video_title: str = Field(..., description="Video title")
    published_at: datetime = Field(..., description="Publication date")
    score: float = Field(..., description="Search relevance score")


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results")


class QuestionRequest(BaseModel):
    query: str = Field(..., description="The question to ask")
    limit: Optional[int] = Field(5, description="Number of results to consider")


class QuestionResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: List[SearchResult] = Field(..., description="Source video segments")
    latest_video: Optional[VideoInfo] = Field(
        None, description="Latest video information"
    )


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
