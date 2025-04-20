import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
from typing import List, Dict


class EmbeddingService:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.storage_dir = Path("storage")
        self.storage_dir.mkdir(exist_ok=True)
        self.metadata = []
        self.latest_video_info = {}
        self.load_index()

    def load_index(self):
        index_path = self.storage_dir / "captions.index"
        metadata_path = self.storage_dir / "metadata.json"
        latest_video_path = self.storage_dir / "latest_video.json"

        if index_path.exists() and metadata_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

        if latest_video_path.exists():
            with open(latest_video_path, "r") as f:
                self.latest_video_info = json.load(f)

    def save_index(self):
        faiss.write_index(self.index, str(self.storage_dir / "captions.index"))
        with open(self.storage_dir / "metadata.json", "w") as f:
            json.dump(self.metadata, f)
        with open(self.storage_dir / "latest_video.json", "w") as f:
            json.dump(self.latest_video_info, f)

    def process_captions(
        self, captions: List[Dict[str, str]], video_id: str, video_info: Dict[str, str]
    ) -> List[Dict[str, str]]:
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

        embeddings = self.embedding_model.encode(chunks)
        self.index.add(np.array(embeddings).astype("float32"))

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

        self.latest_video_info.update(
            {
                "video_id": video_id,
                "title": video_info.get("title", ""),
                "published_at": video_info.get("published_at", ""),
            }
        )

        self.save_index()
        return captions

    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype("float32"), k
        )

        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results
