import json
from pathlib import Path
import pymupdf

MANIFEST = Path("data/book_manifest.json")
BOOK_DIR = Path("data/books")
PAGES_OUT = Path("data/pages.jsonl")
REPORT_OUT = Path("evaluation/ingest_report.json")
GROUP_ID = "G000"  # replace when you know your group ID

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
report = []

with PAGES_OUT.open("w", encoding="utf-8") as out:
    for book in manifest:
        kept = empty = failed = 0
        try:
            with pymupdf.open(BOOK_DIR / book["file"]) as doc:
                for page_no, page in enumerate(doc, start=1):
                    try:
                        text = page.get_text("text").strip()
                    except Exception:
                        failed += 1
                        continue
                    if len(text) < 30:
                        empty += 1
                        continue
                    rec = {
                        "group_id": GROUP_ID,
                        "subject": book["subject"],
                        "book_id": book["book_id"],
                        "title": book["title"],
                        "author": book["author"],
                        "edition": book["edition"],
                        "page": page_no,
                        "text": text,
                    }
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    kept += 1
            book["processing_status"] = "processed"
        except Exception as e:
            book["processing_status"] = f"failed: {e}"
        report.append({"book_id": book["book_id"], "title": book["title"],
                       "pages_kept": kept, "pages_empty": empty,
                       "pages_failed": failed,
                       "status": book["processing_status"]})
        print(book["book_id"], "kept", kept, "empty", empty, "failed", failed)

MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Done. Pages saved to", PAGES_OUT)