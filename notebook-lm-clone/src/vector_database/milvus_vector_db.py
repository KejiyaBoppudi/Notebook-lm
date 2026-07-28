import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import faiss
import numpy as np
import os
import pickle




from src.embeddings.embedding_generator import EmbeddedChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path("data/faiss")
BASE_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = BASE_DIR / "index.bin"
META_PATH = BASE_DIR / "meta.pkl"


class MilvusVectorDB:   # ⬅️ NAME KEPT (DO NOT CHANGE)
    def __init__(
        self,
        collection_name: str = "notebook_lm",
        embedding_dim: int = 384
    ):
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

        if INDEX_PATH.exists():
            self.index = faiss.read_index(str(INDEX_PATH))
            with open(META_PATH, "rb") as f:
                self.data = pickle.load(f)
            logger.info("FAISS index & metadata loaded from disk")
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.data: List[Dict[str, Any]] = []
            logger.info("New FAISS index created")

        logger.info("FAISS initialized (Milvus replaced successfully)")

    # --------- NO-OP (kept for compatibility) ----------
    def create_index(self, *args, **kwargs):
        logger.info("FAISS index ready")

    # --------- INSERT ----------
    def insert_embeddings(self, embedded_chunks: List[EmbeddedChunk]) -> List[str]:
        if not embedded_chunks:
            return []

        vectors = []
        ids = []

        for chunk in embedded_chunks:
            record = chunk.to_vector_db_format()

            vector = np.array(record["vector"], dtype="float32")
            vectors.append(vector)

            record["page_number"] = record.get("page_number") or -1
            record["start_char"] = record.get("start_char") or -1
            record["end_char"] = record.get("end_char") or -1

            self.data.append(record)
            ids.append(record["id"])

        self.index.add(np.vstack(vectors))

        faiss.write_index(self.index, str(INDEX_PATH))
        with open(META_PATH, "wb") as f:
            pickle.dump(self.data, f)
        logger.info(f"Inserted {len(ids)} embeddings into FAISS (persisted)")
        return ids

    # --------- SEARCH ----------
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:

        if self.index.ntotal == 0:
            return []

        query = np.array([query_vector], dtype="float32")
        distances, indices = self.index.search(query, limit)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.data):
                continue

            item = self.data[idx]
            results.append({
                "id": item["id"],
                "score": float(dist),
                "content": item.get("content"),
                "citation": {
                    "source_file": item.get("source_file"),
                    "source_type": item.get("source_type"),
                    "page_number": item.get("page_number"),
                    "chunk_index": item.get("chunk_index"),
                    "start_char": item.get("start_char"),
                    "end_char": item.get("end_char")
                },
                "metadata": item.get("metadata"),
                "embedding_model": item.get("embedding_model")
            })

        return results

    # --------- DELETE ----------
    def delete_collection(self):
        self.index.reset()
        self.data.clear()

        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if META_PATH.exists():
            META_PATH.unlink()
        logger.info("FAISS collection cleared and files deleted")

    # --------- GET BY ID ----------
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        for item in self.data:
            if item["id"] == chunk_id:
                return item
        return None

    # --------- CLOSE ----------
    def close(self):
        logger.info("FAISS closed (no background process)")
