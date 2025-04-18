import google.generativeai as genai
from typing import List, Dict, Any
from app.core.settings import get_settings
from app.models.schemas import SearchResult
from fastapi import HTTPException

settings = get_settings()


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate_answer(
        self,
        query: str,
        context: List[Dict[str, Any]],
        latest_video: Dict[str, Any] = None,
    ) -> str:
        """Generate an answer using Gemini based on the provided context."""
        try:
            # Prepare context
            context_text = "\n\n".join(
                [
                    f"From video '{item['video_title']}' (published {item['published_at']}):\n"
                    f"Timestamp: {item['timestamp']}s\n"
                    f"Content: {item['text']}"
                    for item in context
                ]
            )

            # Prepare prompt
            prompt = f"""You are an AI assistant helping users understand Fireship's YouTube content.
            Use the following context to answer the user's question. If the information is not in the context,
            say so clearly.

            Context:
            {context_text}

            Question: {query}

            Please provide a clear, concise answer based on the context."""

            # Generate response
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate answer: {str(e)}"
            )

    def format_search_results(
        self, results: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Format search results into the expected schema."""
        return [
            SearchResult(
                text=result["text"],
                video_id=result["video_id"],
                timestamp=result["timestamp"],
                video_title=result["video_title"],
                published_at=result["published_at"],
                score=result.get("score", 0.0),
            )
            for result in results
        ]


gemini_service = GeminiService()
