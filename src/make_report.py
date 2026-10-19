import json
from pathlib import Path


def summarize(split):
    rows = json.loads(Path(f"evaluation/results_{split}.json").read_text(encoding="utf-8"))
    ans = [r for r in rows if r["answerable"]]
    noans = [r for r in rows if not r["answerable"]]
    given = [r for r in ans if not r["refused"]]
    marked = [r for r in given if r.get("correct_by_hand (true/false)") in (True, False)]
    return {
        "questions": len(rows),
        "answerable": len(ans),
        "recall_at_5_hits": sum(bool(r.get("recall_at_5_hit")) for r in ans),
        "wrongly_refused": sum(r["refused"] for r in ans),
        "answers_given": len(given),
        "answers_citing_expected_page": sum(bool(r.get("expected_page_cited")) for r in given),
        "answers_marked_by_hand": len(marked),
        "answers_correct_by_hand": sum(bool(r["correct_by_hand (true/false)"]) for r in marked),
        "no_answer_questions": len(noans),
        "no_answer_correctly_refused": sum(r["refused"] for r in noans),
        "avg_seconds_per_question": round(sum(r["seconds"] for r in rows) / max(len(rows), 1), 1),
    }


report = {
    "group_id": "G000",
    "subject": "Machine Learning and Large Language Models",
    "config": json.loads(Path("config/model_config.json").read_text(encoding="utf-8")),
    "validation": summarize("validation"),
    "test": summarize("test"),
    "notes": [
        "Thresholds (min_retrieval_score 0.50) were chosen from six informal questions before the formal evaluation.",
        "min_answer_support was tested at 0.25 on the validation split and gave identical results.",
        "Recall@5 counts only the exact PDF page the question was drawn from.",
        "Some auto-drafted reference answers were flawed, so the correctness score is conservative.",
        "Book permission status is TO_CONFIRM; PDFs and extracted text are not distributed.",
    ],
}
Path("evaluation/report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report["validation"], indent=2))
print(json.dumps(report["test"], indent=2))