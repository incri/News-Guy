from fastapi import APIRouter, HTTPException
from app.services.youtube import YouTubeService
from app.services.embeddings import EmbeddingService
from app.services.gemini import GeminiService
from app.schemas.models import (
    CaptionResponse,
    SearchResponse,
    QueryResponse,
    SearchResult,
)

router = APIRouter()
youtube_service = YouTubeService()
embedding_service = EmbeddingService()
gemini_service = GeminiService()


@router.get("/latest-captions", response_model=CaptionResponse)
async def get_latest_captions() -> CaptionResponse:
    try:
        video_id = youtube_service.get_latest_video_id()
        video_info = youtube_service.get_video_info(video_id)
        transcript = youtube_service.get_transcript(video_id)

        processed_captions = embedding_service.process_captions(
            transcript, video_id, video_info
        )

        return CaptionResponse(
            captions=processed_captions,
            video_id=video_id,
            video_title=video_info.get("title", ""),
            published_at=video_info.get("published_at", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=SearchResponse)
async def search_captions(query: str, k: int = 5) -> SearchResponse:
    try:
        results = embedding_service.search(query, k)
        return SearchResponse(
            results=[
                SearchResult(
                    text=result["text"],
                    video_id=result["video_id"],
                    timestamp=result["timestamp"],
                    video_title=result["video_title"],
                    published_at=result["published_at"],
                )
                for result in results
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ask", response_model=QueryResponse)
async def ask_question(query: str, k: int = 5) -> QueryResponse:
    try:
        search_results = embedding_service.search(query, k)
        context = "\n".join([result["text"] for result in search_results])

        answer = gemini_service.generate_answer(query, context)

        return QueryResponse(
            answer=answer,
            sources=[
                SearchResult(
                    text=result["text"],
                    video_id=result["video_id"],
                    timestamp=result["timestamp"],
                    video_title=result["video_title"],
                    published_at=result["published_at"],
                )
                for result in search_results
            ],
            latest_video_info=embedding_service.latest_video_info,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
