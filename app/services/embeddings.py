import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from pathlib import Path
import json
from app.core.settings import get_settings
from app.models.schemas import CaptionItem
from fastapi import HTTPException

settings = get_settings()


class EmbeddingsService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self._load_index()

    def _load_index(self):
        """Load existing index and metadata if they exist."""
        try:
            if settings.INDEX_PATH.exists() and settings.METADATA_PATH.exists():
                self.index = faiss.read_index(str(settings.INDEX_PATH))
                with open(settings.METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load index: {str(e)}"
            )

    def _save_index(self):
        """Save the FAISS index and metadata to disk."""
        try:
            settings.STORAGE_DIR.mkdir(exist_ok=True)
            faiss.write_index(self.index, str(settings.INDEX_PATH))
            with open(settings.METADATA_PATH, "w") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save index: {str(e)}"
            )

    def process_captions(
        self, captions: List[CaptionItem], video_id: str, video_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process captions and store them in FAISS."""
        try:
            # Combine captions into chunks
            chunks = []
            current_chunk = []
            current_timestamp = 0

            for caption in captions:
                current_chunk.append(caption.text)
                if len(current_chunk) >= settings.CHUNK_SIZE:
                    chunks.append(" ".join(current_chunk))
                    current_timestamp = caption.start
                    current_chunk = []

            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_timestamp = captions[-1].start

            # Generate embeddings
            embeddings = self.model.encode(chunks)

            # Add to FAISS index
            self.index.add(np.array(embeddings).astype("float32"))

            # Update metadata
            for chunk in chunks:
                self.metadata.append(
                    {
                        "text": chunk,
                        "video_id": video_id,
                        "timestamp": current_timestamp,
                        "video_title": video_info.get("title", ""),
                        "published_at": video_info.get("published_at", ""),
                    }
                )

            # Save to disk
            self._save_index()

            return self.metadata
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to process captions: {str(e)}"
            )

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content using FAISS."""
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])

            # Search in FAISS index
            distances, indices = self.index.search(
                np.array(query_embedding).astype("float32"), k
            )

            # Get results from metadata
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result["score"] = float(distance)
                    results.append(result)

            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


embeddings_service = EmbeddingsService()
