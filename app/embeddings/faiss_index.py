import faiss
import numpy as np
import os
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class FaissSearchEngine:
    def __init__(self, dimension: int = 384, index_path: str = "/app/uploads/faiss_index.bin"):
        """
        Initialize FAISS index. Dimension 384 matches 'all-MiniLM-L6-v2' output.
        """
        self.dimension = dimension
        self.index_path = index_path
        
        # L2 Distance Index (Cosine similarity equivalent if vectors are normalized)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.candidate_ids: List[int] = []
        
        self.load_index()

    def add_vector(self, candidate_id: int, vector: np.ndarray):
        """Adds a normalized candidate embedding to the FAISS index."""
        # Ensure shape is (1, d) and float32
        vec_np = np.array([vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        
        self.index.add(vec_np)
        self.candidate_ids.append(candidate_id)
        self.save_index()
        logger.info(f"Added candidate {candidate_id} to FAISS index. Total: {self.index.ntotal}")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """Searches the index for the most similar candidates to a job query."""
        if self.index.ntotal == 0:
            return []

        vec_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        
        # D is distances, I is indices
        distances, indices = self.index.search(vec_np, top_k)
        
        results = []
        for j, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.candidate_ids):
                # Convert L2 distance to a similarity score (approximate)
                similarity = max(0.0, 1.0 - (distances[0][j] / 2.0)) 
                results.append((self.candidate_ids[idx], similarity))
                
        return results

    def save_index(self):
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info("Loaded existing FAISS index.")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")