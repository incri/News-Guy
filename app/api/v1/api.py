from fastapi import APIRouter
from app.api.v1.endpoints import captions, search, questions

api_router = APIRouter()

api_router.include_router(captions.router, prefix="/captions", tags=["captions"])

api_router.include_router(search.router, prefix="/search", tags=["search"])

api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
