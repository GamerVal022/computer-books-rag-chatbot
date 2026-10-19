import json, re
from pathlib import Path
import pymupdf

GROUP_ID = "G000"  # replace when you know your group ID
SUBJECT = "Machine Learning and Large Language Models"
BOOK_DIR = Path("data/books")
OUT = Path("data/book_manifest.json")


def guess(stem):
    s = stem.replace("_OceanofPDF.com_", "")
    s = re.sub(r"\s*\(\d+\)$", "", s).replace("_", " ").strip()
    parts = [p.strip() for p in s.split(" - ")]
    if len(parts) >= 2:
        return parts[0], parts[-1], " - ".join(parts[1:-1])
    return s, "", ""


def source_type(doc):
    n = len(doc)
    idx = sorted(set(int(i * (n - 1) / 9) for i in range(10))) if n > 1 else [0]
    chars = sum(len(doc[i].get_text()) for i in idx)
    return "PDF text" if chars / len(idx) > 200 else "scanned PDF"


books = []
for i, f in enumerate(sorted(BOOK_DIR.glob("*.pdf")), start=1):
    title, author, edition = guess(f.stem)
    entry = {
        "book_id": f"{GROUP_ID}_BOOK_{i:03d}",
        "file": f.name,
        "title": title,
        "author": author,
        "edition": edition,
        "publisher": "",
        "year": "",
        "isbn": "",
        "subject": SUBJECT,
        "source_type": "",
        "pages": 0,
        "permission_status": "TO_CONFIRM",
        "processing_status": "pending",
    }
    try:
        with pymupdf.open(f) as doc:
            entry["pages"] = len(doc)
            entry["source_type"] = source_type(doc)
    except Exception as e:
        entry["processing_status"] = f"failed: {e}"
    books.append(entry)
    print(entry["book_id"], entry["pages"], entry["source_type"], "|", title)

OUT.write_text(json.dumps(books, indent=2), encoding="utf-8")
print("Saved", OUT, "with", len(books), "books")