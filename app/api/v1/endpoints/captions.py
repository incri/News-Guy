from fastapi import APIRouter, Depends, HTTPException
from app.core.security import validate_api_key
from app.services.youtube import youtube_service
from app.services.embeddings import embeddings_service
from app.models.schemas import CaptionResponse, ErrorResponse
from typing import Union

router = APIRouter()


@router.get(
    "/latest-captions",
    response_model=Union[CaptionResponse, ErrorResponse],
    summary="Get latest video captions",
    description="Fetches and processes captions from the latest Fireship video",
    responses={
        200: {"description": "Successfully retrieved captions"},
        401: {"description": "Unauthorized"},
        404: {"description": "Video or captions not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_latest_captions(
    api_key: str = Depends(validate_api_key),
) -> Union[CaptionResponse, ErrorResponse]:
    """Get captions from the latest Fireship video and store them in FAISS."""
    try:
        # Get the latest video ID
        video_id = await youtube_service.get_latest_video_id()

        # Get video information
        video_info = await youtube_service.get_video_info(video_id)

        # Get the transcript
        captions = await youtube_service.get_transcript(video_id)

        # Process and store captions
        processed_metadata = embeddings_service.process_captions(
            captions, video_id, video_info.dict()
        )

        return CaptionResponse(captions=captions, video_info=video_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
