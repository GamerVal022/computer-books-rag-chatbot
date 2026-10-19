import json
import re
from pathlib import Path

PAGES_IN = Path("data/pages.jsonl")
CHUNKS_OUT = Path("data/chunks.jsonl")
CHUNK_WORDS = 250   # target passage size
OVERLAP = 40        # words shared between neighbouring passages
MIN_WORDS = 30      # drop tiny fragments


def clean(text):
    text = re.sub(r"-\n(\w)", r"\1", text)   # join words split across lines
    text = re.sub(r"\s*\n\s*", " ", text)    # newlines to spaces
    return re.sub(r"\s+", " ", text).strip()


total = 0
with PAGES_IN.open(encoding="utf-8") as f, CHUNKS_OUT.open("w", encoding="utf-8") as out:
    for line in f:
        rec = json.loads(line)
        words = clean(rec["text"]).split()
        if len(words) < MIN_WORDS:
            continue
        start, c = 0, 1
        while start < len(words):
            piece = words[start:start + CHUNK_WORDS]
            if len(piece) < MIN_WORDS and c > 1:
                break
            chunk = {
                "group_id": rec["group_id"],
                "subject": rec["subject"],
                "book_id": rec["book_id"],
                "title": rec["title"],
                "author": rec["author"],
                "edition": rec["edition"],
                "page": rec["page"],
                "chunk_id": f'{rec["book_id"]}_P{rec["page"]}_C{c:02d}',
                "text": " ".join(piece),
            }
            out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            total += 1
            c += 1
            if start + CHUNK_WORDS >= len(words):
                break
            start += CHUNK_WORDS - OVERLAP

print("Chunks written:", total, "->", CHUNKS_OUT)