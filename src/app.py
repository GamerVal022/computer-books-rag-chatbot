import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from generate import answer
from retrieve import retrieve

st.set_page_config(page_title="Book Chatbot", page_icon="📚")
st.title("📚 ML & LLM Book Chatbot")
st.caption("Answers come only from the 20 indexed books, with citations (PDF page numbers).")

question = st.text_input("Ask a question about machine learning or LLMs:")

if question:
    with st.spinner("Searching the books and writing an answer..."):
        result = answer(question)
        passages = {p["chunk_id"]: p for p in retrieve(question, 5)}

    if result["insufficient_evidence"]:
        st.warning(result["answer"])
    else:
        st.subheader("Answer")
        st.write(result["answer"])
        st.subheader("Sources")
        for s in result["sources"]:
            with st.expander(f'{s["title"]} (PDF page {s["page"]}) [{s["chunk_id"]}]'):
                p = passages.get(s["chunk_id"])
                st.write(p["text"] if p else "Passage text not available.")