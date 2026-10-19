import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generate import answer
from retrieve import retrieve

REQUIRED = {"group_id", "subject", "book_id", "title", "page", "chunk_id", "text", "edition"}
CHUNK_IDS = set()
with open("data/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        assert REQUIRED <= rec.keys()
        CHUNK_IDS.add(rec["chunk_id"])


def test_retrieve_returns_metadata():
    results = retrieve("What is self-attention in a transformer?", top_k=5)
    assert len(results) == 5
    for r in results:
        assert {"text", "score", "book_id", "title", "page", "chunk_id"} <= r.keys()


def test_citations_resolve_to_real_passages():
    result = answer("What is self-attention in a transformer?")
    assert not result["insufficient_evidence"]
    assert result["sources"]
    for s in result["sources"]:
        assert s["chunk_id"] in CHUNK_IDS


def test_answer_format():
    result = answer("What is overfitting?")
    assert set(result.keys()) == {"answer", "sources", "insufficient_evidence"}
    for s in result["sources"]:
        assert {"book_id", "page", "chunk_id"} <= s.keys()


def test_abstains_when_books_lack_evidence():
    result = answer("How do I bake bread?")
    assert result["insufficient_evidence"] is True
    assert result["sources"] == []