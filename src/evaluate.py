import json
import sys
import time
from pathlib import Path

from retrieve import retrieve
from generate import answer

split = sys.argv[1] if len(sys.argv) > 1 else "validation"
all_q = json.loads(Path("data/evaluation_questions.json").read_text(encoding="utf-8"))
data = [d for d in all_q if d["split"] == split]
rows, times = [], []
hits = ans_n = false_ref = cite_n = cite_ok = noans_n = refused_ok = 0

for d in data:
    t = time.time()
    res = answer(d["question"])
    dt = time.time() - t
    times.append(dt)
    refused = res["insufficient_evidence"]
    row = {"id": d["id"], "question": d["question"], "answerable": d["answerable"],
           "answer": res["answer"], "refused": refused,
           "sources": res["sources"], "seconds": round(dt, 1)}
    if d["answerable"]:
        ans_n += 1
        top = retrieve(d["question"], 5)
        hit = any(p["book_id"] == d["expected_book_id"] and p["page"] == d["expected_page"]
                  for p in top)
        hits += hit
        row["recall_at_5_hit"] = bool(hit)
        row["reference_answer"] = d["reference_answer"]
        if refused:
            false_ref += 1
        else:
            cite_n += 1
            ok = any(s["book_id"] == d["expected_book_id"] and s["page"] == d["expected_page"]
                     for s in res["sources"])
            cite_ok += ok
            row["expected_page_cited"] = bool(ok)
            row["correct_by_hand (true/false)"] = ""
    else:
        noans_n += 1
        refused_ok += refused
    rows.append(row)
    print(d["id"], "done")

out = Path(f"evaluation/results_{split}.json")
out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
print(f"\nSPLIT: {split}  ({len(data)} questions)")
if ans_n:
    print(f"Recall@5 (answerable): {hits}/{ans_n} = {hits / ans_n:.0%}")
    print(f"Wrongly refused answerable questions: {false_ref}/{ans_n}")
if cite_n:
    print(f"Answers citing the expected page: {cite_ok}/{cite_n}")
if noans_n:
    print(f"Correctly refused no-answer questions: {refused_ok}/{noans_n} = {refused_ok / noans_n:.0%}")
print(f"Average seconds per question: {sum(times) / max(len(times), 1):.1f}")
print("Details saved to", out)