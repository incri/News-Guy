from pydantic import BaseModel
from typing import List, Dict


class CaptionItem(BaseModel):
    text: str
    start: float
    duration: float


class CaptionResponse(BaseModel):
    captions: List[CaptionItem]
    video_id: str
    video_title: str
    published_at: str


class SearchResult(BaseModel):
    text: str
    video_id: str
    timestamp: float
    video_title: str
    published_at: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


class QueryResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    latest_video_info: Dict[str, str]
