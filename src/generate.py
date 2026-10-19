import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from retrieve import retrieve, _get_model

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MIN_SCORE = 0.50     # below this the books are treated as not covering the question
SUPPORT_MIN = 0.35   # minimum similarity between the answer and a passage to cite it
TOP_K = 5
_tok = _model = None

SYSTEM = ("You answer questions using ONLY the numbered passages provided. "
          "If the passages do not contain the answer, reply exactly: INSUFFICIENT EVIDENCE. "
          "Never invent facts.")

NO_EVIDENCE = {"answer": "The provided books do not contain sufficient evidence to answer this.",
               "sources": [], "insufficient_evidence": True}


def _load():
    global _tok, _model
    if _model is None:
        REV = "7ae557604adf67be50417f59c2c2f167def9a775"
        _tok = AutoTokenizer.from_pretrained(MODEL_NAME, revision=REV)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, revision=REV, dtype=torch.float32)
        _model.eval()
    return _tok, _model


def answer(question, top_k=TOP_K):
    passages = retrieve(question, top_k)
    if not passages or passages[0]["score"] < MIN_SCORE:
        return dict(NO_EVIDENCE)
    context = "\n\n".join(
        f"[{i}] ({p['title']}, PDF page {p['page']}) {p['text']}"
        for i, p in enumerate(passages, 1))
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"}]
    tok, model = _load()
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=250, do_sample=False)
    text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    if not text or "INSUFFICIENT EVIDENCE" in text.upper():
        return dict(NO_EVIDENCE)
    # keep only passages whose meaning is close to the answer
    emb = _get_model()
    a_vec = emb.encode([text], normalize_embeddings=True, convert_to_numpy=True)[0]
    p_vecs = emb.encode([p["text"] for p in passages], normalize_embeddings=True,
                        convert_to_numpy=True)
    sims = p_vecs @ a_vec
    used = [p for p, s in zip(passages, sims) if s >= SUPPORT_MIN]
    if not used:
        return dict(NO_EVIDENCE)
    sources = [{"book_id": p["book_id"], "title": p["title"], "page": p["page"],
                "chunk_id": p["chunk_id"]} for p in used]
    return {"answer": text, "sources": sources, "insufficient_evidence": False}


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is self-attention?"
    print(answer(q))