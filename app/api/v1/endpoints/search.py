from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import validate_api_key
from app.services.embeddings import embeddings_service
from app.services.gemini import gemini_service
from app.models.schemas import SearchResponse, ErrorResponse
from typing import Union

router = APIRouter()


@router.get(
    "/search",
    response_model=Union[SearchResponse, ErrorResponse],
    summary="Search video content",
    description="Search through processed video content using semantic search",
    responses={
        200: {"description": "Successfully retrieved search results"},
        401: {"description": "Unauthorized"},
        404: {"description": "No results found"},
        500: {"description": "Internal server error"},
    },
)
async def search_content(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Number of results to return"),
    api_key: str = Depends(validate_api_key),
) -> Union[SearchResponse, ErrorResponse]:
    """Search through processed video content using semantic search."""
    try:
        # Perform semantic search
        results = embeddings_service.search(query, k=limit)

        if not results:
            raise HTTPException(
                status_code=404, detail="No results found for the given query"
            )

        # Format results
        formatted_results = gemini_service.format_search_results(results)

        return SearchResponse(
            results=formatted_results, total_results=len(formatted_results)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
