"""
rag.py — RAG retrieval using ChromaDB's built-in ONNX embedding model.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DB_PATH, COLLECTION_NAME, TOP_K_RESULTS

_collection = None   # module-level cache


def get_collection():
    global _collection
    if _collection is None:
        ef     = embedding_functions.DefaultEmbeddingFunction()
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def retrieve_context(query: str):
    """
    Embed the query and return the top-k most relevant medical text chunks.

    Returns
    -------
    context : str        — concatenated relevant passages
    sources : list[str]  — unique source file names
    """
    try:
        col  = get_collection()
        results = col.query(
            query_texts=[query],
            n_results=TOP_K_RESULTS,
            include=["documents", "metadatas"],
        )

        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs:
            return "", []

        context_parts = docs
        sources = []
        for m in metas:
            src = m.get("source", "Medical Knowledge Base")
            if src not in sources:
                sources.append(src)

        return "\n\n---\n\n".join(context_parts), sources

    except Exception as exc:
        print(f"[RAG] Warning: retrieval failed — {exc}")
        return "", []
