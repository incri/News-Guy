from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, List
import os
from dotenv import load_dotenv
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path
from pydantic import BaseModel
import google.generativeai as genai
from datetime import datetime
from fastapi.responses import RedirectResponse

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="News Guy API",
)


# Define response models
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


# YouTube API setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("Please set YOUTUBE_API_KEY in .env file")

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Initialize FAISS and model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384  # Dimension of the embeddings
index = faiss.IndexFlatL2(dimension)

# Create storage directory if it doesn't exist
storage_dir = Path("storage")
storage_dir.mkdir(exist_ok=True)

# File paths
index_path = storage_dir / "captions.index"
metadata_path = storage_dir / "metadata.json"
latest_video_path = storage_dir / "latest_video.json"

# Load existing index and metadata if they exist
if index_path.exists() and metadata_path.exists():
    index = faiss.read_index(str(index_path))
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
else:
    metadata = []

# Load latest video info
if latest_video_path.exists():
    with open(latest_video_path, "r") as f:
        latest_video_info = json.load(f)
else:
    latest_video_info = {}


def save_index_and_metadata():
    """Save the FAISS index and metadata to disk."""
    faiss.write_index(index, str(index_path))
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
    with open(latest_video_path, "w") as f:
        json.dump(latest_video_info, f)


def get_latest_video_id(channel_id: str = "@Fireship") -> str:
    """Get the latest video ID from a YouTube channel."""
    try:
        # First, get the channel ID from the handle
        channel_response = (
            youtube.search()
            .list(part="snippet", q=channel_id, type="channel", maxResults=1)
            .execute()
        )

        if not channel_response["items"]:
            raise HTTPException(status_code=404, detail="Channel not found")

        channel_id = channel_response["items"][0]["id"]["channelId"]

        # Get the latest video
        video_response = (
            youtube.search()
            .list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=1,
            )
            .execute()
        )

        if not video_response["items"]:
            raise HTTPException(status_code=404, detail="No videos found")

        return video_response["items"][0]["id"]["videoId"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_video_info(video_id: str) -> Dict[str, str]:
    """Get video information from YouTube API."""
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()

        if not response["items"]:
            return {}

        video = response["items"][0]
        return {
            "title": video["snippet"]["title"],
            "published_at": video["snippet"]["publishedAt"],
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {}


def process_captions(
    captions: List[Dict[str, str]], video_id: str, video_info: Dict[str, str]
) -> List[Dict[str, str]]:
    """Process captions and store them in FAISS."""
    # Combine captions into chunks for better context
    chunk_size = 5
    chunks = []
    current_chunk = []
    current_timestamp = 0

    for caption in captions:
        current_chunk.append(caption["text"])
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_timestamp = caption["start"]
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))
        current_timestamp = captions[-1]["start"]

    # Generate embeddings for chunks
    embeddings = embedding_model.encode(chunks)

    # Add to FAISS index
    index.add(np.array(embeddings).astype("float32"))

    # Update metadata
    for chunk in chunks:
        metadata.append(
            {
                "text": chunk,
                "video_id": video_id,
                "timestamp": current_timestamp,
                "video_title": video_info.get("title", ""),
                "published_at": video_info.get("published_at", ""),
            }
        )

    # Update latest video info
    latest_video_info.update(
        {
            "video_id": video_id,
            "title": video_info.get("title", ""),
            "published_at": video_info.get("published_at", ""),
        }
    )

    # Save to disk
    save_index_and_metadata()

    return captions


@app.get(
    "/latest-captions",
    operation_id="fetch_latest_captions",
    response_model=CaptionResponse,
)
async def get_latest_captions() -> CaptionResponse:
    """Get captions from the latest Fireship video and store them in FAISS."""
    try:
        # Get the latest video ID
        video_id = get_latest_video_id()

        # Get video information
        video_info = get_video_info(video_id)

        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Process and store captions
        processed_captions = process_captions(transcript, video_id, video_info)

        return CaptionResponse(
            captions=processed_captions,
            video_id=video_id,
            video_title=video_info.get("title", ""),
            published_at=video_info.get("published_at", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", operation_id="search_captions", response_model=SearchResponse)
async def search_captions(query: str, k: int = 5) -> SearchResponse:
    """Search through stored captions using FAISS."""
    try:
        # Generate embedding for the query
        query_embedding = embedding_model.encode([query])

        # Search in FAISS index
        distances, indices = index.search(
            np.array(query_embedding).astype("float32"), k
        )

        # Get results from metadata
        results = []
        for idx in indices[0]:
            if idx < len(metadata):
                results.append(SearchResult(**metadata[idx]))

        return SearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask", operation_id="ask_question", response_model=QueryResponse)
async def ask_question(query: str, k: int = 5) -> QueryResponse:
    """Ask a question and get an answer using Gemini with relevant context from FAISS."""
    try:
        # First, get relevant context from FAISS
        query_embedding = embedding_model.encode([query])
        distances, indices = index.search(
            np.array(query_embedding).astype("float32"), k
        )

        # Get relevant context
        context = []
        sources = []
        latest_video_context = []

        for idx in indices[0]:
            if idx < len(metadata):
                item = metadata[idx]
                sources.append(SearchResult(**item))
                context.append(item["text"])

                # If this is from the latest video, add to special context
                if item["video_id"] == latest_video_info.get("video_id"):
                    latest_video_context.append(item["text"])

        if not context:
            return QueryResponse(
                answer="I couldn't find any relevant information in the stored captions. Please try fetching the latest video captions first.",
                sources=[],
                latest_video_info=latest_video_info,
            )

        # Prepare the prompt for Gemini
        prompt = f"""You are an AI assistant that answers questions based on YouTube video captions.
        Please provide a clear and concise answer to the question based on the context provided.
        If the answer cannot be found in the context, say "I couldn't find relevant information in the available context."

        Context from YouTube video captions:
        {' '.join(context)}

        Question: {query}

        Please provide a direct answer to the question:"""

        # Generate response using Gemini
        response = model.generate_content(prompt)

        return QueryResponse(
            answer=response.text, sources=sources, latest_video_info=latest_video_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


mcp = FastApiMCP(
    app,
    name="News Guy MCP Server",  # Name for your MCP server
    description="MCP server for News Guy API",  # Description
    base_url="http://localhost:8000",  # Where your API is running
    describe_all_responses=True,  # Include all possible response schemas
    describe_full_response_schema=True,  # Include full JSON schema in descriptions
)

# Mount the MCP server to your FastAPI app
mcp.mount()
