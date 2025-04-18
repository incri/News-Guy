from fastapi import APIRouter, Depends, HTTPException
from app.core.security import validate_api_key
from app.services.embeddings import embeddings_service
from app.services.gemini import gemini_service
from app.services.youtube import youtube_service
from app.models.schemas import QuestionRequest, QuestionResponse, ErrorResponse
from typing import Union

router = APIRouter()


@router.post(
    "/ask",
    response_model=Union[QuestionResponse, ErrorResponse],
    summary="Ask a question",
    description="Ask a question about the video content using Gemini",
    responses={
        200: {"description": "Successfully generated answer"},
        401: {"description": "Unauthorized"},
        404: {"description": "No relevant content found"},
        500: {"description": "Internal server error"},
    },
)
async def ask_question(
    request: QuestionRequest, api_key: str = Depends(validate_api_key)
) -> Union[QuestionResponse, ErrorResponse]:
    """Ask a question about the video content using Gemini."""
    try:
        # Search for relevant content
        search_results = embeddings_service.search(request.query, k=request.limit)

        if not search_results:
            raise HTTPException(
                status_code=404, detail="No relevant content found for the question"
            )

        # Get latest video info
        latest_video_id = await youtube_service.get_latest_video_id()
        latest_video_info = await youtube_service.get_video_info(latest_video_id)

        # Generate answer
        answer = await gemini_service.generate_answer(
            request.query, search_results, latest_video_info.dict()
        )

        # Format search results
        formatted_results = gemini_service.format_search_results(search_results)

        return QuestionResponse(
            answer=answer, sources=formatted_results, latest_video=latest_video_info
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
