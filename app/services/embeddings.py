import faiss
import numpy as np
from typing import List, Tuple
import os
from app.config import get_settings

settings = get_settings()


class EmbeddingsService:
    def __init__(
        self, dimension: int = 768
    ):  # Default dimension for most embedding models
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(settings.faiss_index_path), exist_ok=True)

    def add_embeddings(self, embeddings: np.ndarray, ids: List[int]):
        """Add embeddings to the FAISS index."""
        self.index.add(embeddings)

    def search(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar embeddings."""
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices

    def save_index(self):
        """Save the FAISS index to disk."""
        faiss.write_index(self.index, settings.faiss_index_path)

    def load_index(self):
        """Load the FAISS index from disk if it exists."""
        if os.path.exists(settings.faiss_index_path):
            self.index = faiss.read_index(settings.faiss_index_path)
