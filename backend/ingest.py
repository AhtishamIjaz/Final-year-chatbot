"""
ingest.py — Load medical knowledge base into ChromaDB.
Uses ChromaDB's built-in ONNX embedding model (no API key, no extra downloads).
Run ONCE before starting the server:  python ingest.py
"""

import os
import sys
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DB_PATH, COLLECTION_NAME


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list:
    """Simple sliding-window text chunker."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest():
    print("\n" + "=" * 54)
    print("   MedGPT — Medical Knowledge Base Ingestion")
    print("=" * 54 + "\n")

    # Locate knowledge_base/ (one level up from backend/)
    kb_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    if not kb_dir.exists():
        print(f"[ERROR] knowledge_base/ not found at: {kb_dir}")
        sys.exit(1)

    # Remove old ChromaDB to avoid duplicates
    chroma_path = Path(CHROMA_DB_PATH)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        print("  Cleared old ChromaDB.\n")

    # Connect to ChromaDB with built-in embedding model
    print("  Using ChromaDB built-in ONNX embedding model...")
    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Load + chunk all .txt files
    all_docs, all_ids, all_meta = [], [], []
    doc_id = 0

    txt_files = sorted(kb_dir.glob("*.txt"))
    print(f"  Loading {len(txt_files)} knowledge-base files:\n")

    for txt_file in txt_files:
        content = txt_file.read_text(encoding="utf-8")
        chunks  = chunk_text(content)
        print(f"    {txt_file.name:35s} -> {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_docs.append(chunk)
            all_ids.append(f"doc_{doc_id}_{i}")
            all_meta.append({
                "source":   txt_file.name,
                "filename": txt_file.name,
                "chunk":    i,
            })
        doc_id += 1

    print(f"\n  Total chunks to embed: {len(all_docs)}")
    print("  Embedding & storing (may take ~30 s on first run)...\n")

    # Upsert in batches of 50
    batch = 50
    for i in range(0, len(all_docs), batch):
        collection.upsert(
            documents=all_docs[i:i+batch],
            ids=all_ids[i:i+batch],
            metadatas=all_meta[i:i+batch],
        )
        done = min(i + batch, len(all_docs))
        print(f"    Stored {done}/{len(all_docs)} chunks...")

    print(f"\n[OK] Ingestion complete — {len(all_docs)} chunks in ChromaDB!")
    print(f"     Path: {chroma_path.resolve()}")
    print("\nYou can now start the server:  python main.py\n")


if __name__ == "__main__":
    ingest()
