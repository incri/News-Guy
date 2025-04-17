from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database.session import get_db
from app.database.models import Video
from app.services.youtube import YouTubeService
from app.services.embeddings import EmbeddingsService
from app.services.gemini import GeminiService

router = APIRouter()
youtube_service = YouTubeService()
embeddings_service = EmbeddingsService()
gemini_service = GeminiService()


class VideoResponse(BaseModel):
    video_id: str
    title: str
    description: str
    published_at: datetime
    link: str


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]


@router.get("/videos", response_model=List[VideoResponse])
async def list_videos(db: Session = Depends(get_db)):
    """List all videos in the database."""
    try:
        videos = db.query(Video).all()
        return [
            VideoResponse(
                video_id=video.video_id,
                title=video.title,
                description=video.description,
                published_at=video.published_at,
                link=video.link,
            )
            for video in videos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get details of a specific video."""
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        return VideoResponse(
            video_id=video.video_id,
            title=video.title,
            description=video.description,
            published_at=video.published_at,
            link=video.link,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_videos(request: QueryRequest, db: Session = Depends(get_db)):
    """Query videos using natural language."""
    try:
        # 1. Get latest videos
        videos = youtube_service.get_latest_videos()

        # 2. Process each video
        context = []
        for video in videos:
            video_id = video["id"]["videoId"]

            # Get video details and captions
            details = youtube_service.get_video_details(video_id)
            captions = youtube_service.get_captions(video_id)

            if captions:
                context.append(
                    {
                        "source": "video_caption",
                        "content": captions,
                        "metadata": {
                            "video_id": video_id,
                            "title": details["snippet"]["title"],
                            "published_at": details["snippet"]["publishedAt"],
                        },
                    }
                )

        # 3. Generate response using Gemini
        answer = gemini_service.generate_response(context, request.query)

        # 4. Return response
        return QueryResponse(
            answer=answer, sources=[item["metadata"] for item in context]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
