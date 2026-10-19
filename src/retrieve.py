import json
import sys
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # small, laptop-friendly
MAX_SEQ_LENGTH = 384
CHUNKS = Path("data/chunks.jsonl")
INDEX_FILE = Path("artifacts/faiss.index")
CONFIG_FILE = Path("config/retrieval_config.json")

_model = None
_index = None
_chunks = None


def _load_chunks():
    global _chunks
    if _chunks is None:
        with CHUNKS.open(encoding="utf-8") as f:
            _chunks = [json.loads(line) for line in f]
    return _chunks


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME, revision="1110a243fdf4706b3f48f1d95db1a4f5529b4d41")
        _model.max_seq_length = MAX_SEQ_LENGTH
    return _model


def build_index():
    chunks = _load_chunks()
    texts = [c["text"] for c in chunks]
    emb = _get_model().encode(
        texts, batch_size=32, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    ).astype("float32")
    index = faiss.IndexFlatIP(emb.shape[1])  # cosine similarity (vectors are normalized)
    index.add(emb)
    INDEX_FILE.parent.mkdir(exist_ok=True)
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    CONFIG_FILE.write_text(json.dumps({
        "embedding_model": MODEL_NAME,
        "model_revision": "FILL_IN_FROM_CACHE",
        "max_seq_length": MAX_SEQ_LENGTH,
        "index_type": "faiss IndexFlatIP, normalized embeddings",
        "num_chunks": len(chunks),
        "chunk_words": 250,
        "chunk_overlap_words": 40,
    }, indent=2), encoding="utf-8")
    print("Index built with", len(chunks), "chunks")


def retrieve(question: str, top_k: int = 5) -> list:
    """Return passages with text, score, book_id, title, page, and chunk_id."""
    global _index
    if _index is None:
        _index = faiss.read_index(str(INDEX_FILE))
    q = _get_model().encode([question], normalize_embeddings=True,
                            convert_to_numpy=True).astype("float32")
    scores, ids = _index.search(q, top_k)
    chunks = _load_chunks()
    results = []
    for score, i in zip(scores[0], ids[0]):
        if i < 0:
            continue
        c = chunks[i]
        results.append({
            "text": c["text"], "score": float(score),
            "book_id": c["book_id"], "title": c["title"], "author": c["author"],
            "edition": c["edition"], "page": c["page"], "chunk_id": c["chunk_id"],
        })
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build_index()
    else:
        question = " ".join(sys.argv[1:]) or "What is self-attention?"
        for r in retrieve(question):
            print(f'{r["score"]:.3f} | {r["title"]} | PDF page {r["page"]} | {r["chunk_id"]}')
            print("   ", r["text"][:200], "...\n")