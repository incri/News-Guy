import google.generativeai as genai
from app.config import Config


class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def generate_answer(self, prompt: str, context: str) -> str:
        try:
            response = self.model.generate_content(
                f"""Context: {context}
                
                Question: {prompt}
                
                Answer based on the context above:"""
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")
