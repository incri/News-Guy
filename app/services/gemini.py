import google.generativeai as genai
from app.config import get_settings
from typing import List, Dict, Any

settings = get_settings()


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        for text in texts:
            response = self.model.embed_content(text)
            embeddings.append(response["embedding"])
        return embeddings

    def generate_response(self, context: List[Dict[str, Any]], query: str) -> str:
        """Generate a response based on context and query."""
        prompt = self._construct_prompt(context, query)
        response = self.model.generate_content(prompt)
        return response.text

    def _construct_prompt(self, context: List[Dict[str, Any]], query: str) -> str:
        """Construct a prompt from context and query."""
        context_str = "\n".join(
            [
                f"Source: {item['source']}\nContent: {item['content']}\n"
                for item in context
            ]
        )
        return f"""Context:
{context_str}

Query: {query}

Please provide a detailed answer based on the context above."""
