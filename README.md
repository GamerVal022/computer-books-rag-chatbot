# Computer Books RAG Chatbot

## 1. Project Information

- **Group Members:** Kuunda Banda and Bwalya Musonda
- **Student Numbers:** 202502965 and 202503581
- **Project Type:** Retrieval-Augmented Generation (RAG) Chatbot
- **Programming Language:** Python 3.12
- **User Interface:** Streamlit

## 2. Project Overview

The Computer Books RAG Chatbot is a question-answering application that uses a collection of computer-related books to help users find information and understand computer science concepts.

The system extracts text from books, divides the text into smaller chunks, converts the chunks into numerical embeddings, and retrieves relevant passages when a user asks a question. A language model then generates an answer based on the retrieved information.

The chatbot provides source citations, including book titles and page references where available. It is designed to avoid answering questions when the available evidence is insufficient.

## 3. Main Features

- Book ingestion and text extraction.
- Text chunking with metadata preservation.
- Semantic search using sentence embeddings.
- Vector similarity search using FAISS.
- Transformer-based answer generation.
- Source citations for retrieved passages.
- Streamlit interface for interacting with the chatbot.
- Evaluation using reference questions and answers.
- Testing of retrieval, answer formatting, citations, and insufficient-evidence handling.

## 4. System Architecture

The chatbot follows a Retrieval-Augmented Generation workflow:

1. **Book ingestion:** Extract text and associated metadata from the computer books.
2. **Text chunking:** Divide extracted text into smaller passages while retaining relevant metadata.
3. **Embedding generation:** Convert passages into vector representations using a sentence-transformer model.
4. **Indexing:** Store the vectors in a FAISS index for similarity-based retrieval.
5. **Question retrieval:** Retrieve relevant passages in response to a user's question.
6. **Answer generation:** Use a language model to generate an answer grounded in the retrieved evidence.
7. **Citation and response:** Present the generated answer with available source references.

## 5. Technologies and Models

- **Programming Language:** Python 3.12
- **User Interface:** Streamlit
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Generation Model:** `Qwen/Qwen2.5-0.5B-Instruct`
- **Vector Search:** FAISS
- **Model Framework:** Transformers and Sentence Transformers

### Model Configuration

- **Generation Model Revision:** `7ae557604adf67be50417f59c2c2f167def9a775`
- **Embedding Model Revision:** `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`
- **Chunk Size:** 250 words
- **Chunk Overlap:** 40 words
- **Retrieval Top-K:** 5
- **Minimum Retrieval Score:** 0.50
- **Minimum Answer Support:** 0.35
- **Execution:** CPU-based inference

The configured thresholds are used to help determine whether retrieved evidence is sufficiently relevant to support an answer. They do not guarantee that every generated answer is correct.

## 6. Project Structure

The main project directories and files are organized as follows:

```text
Computer_Books_Chatbot/
├── config/
│   └── retrieval_config.json
├── data/
│   ├── books/
│   ├── book_manifest.json
│   └── evaluation_questions.json
├── artifacts/
├── evaluation/
│   └── report.json
├── src/
│   ├── ingest.py
│   ├── chunk.py
│   ├── retrieve.py
│   ├── generate.py
│   ├── app.py
│   └── make_report.py
├── tests/
├── requirements.txt
└── README.md
```

This tree describes the principal project components. Some generated files and supporting files may vary depending on the local setup.

## 7. Installation and Setup

### Prerequisites

- Python 3.12
- Internet access for downloading dependencies and model files when they are not already available locally.
- Sufficient disk space and memory for the models, books, and retrieval index.

### Step 1: Open the Project Directory

Open PowerShell and navigate to the project folder:

```powershell
cd "$HOME\Documents\Computer_Books_Chatbot"
```

### Step 2: Create a Virtual Environment

If a virtual environment has not already been created, run:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Install the packages listed in the requirements file:

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Prepare the Retrieval Index

Ensure the book collection and configuration files are in place. Build the retrieval index using the project's supported index-building procedure.

If the implementation supports the following command, use:

```powershell
python src\retrieve.py build
```

Otherwise, follow the index-building procedure defined by the actual project code.

### Step 5: Launch the Application

Once the dependencies and retrieval index are ready, launch the Streamlit interface:

```powershell
streamlit run src\app.py
```

The application can then be accessed through the local address provided by Streamlit.

**Note:** The first run may require additional time and disk space to download model files.

## 8. Testing

Automated tests were executed using:

```powershell
python -m pytest tests -v
```

**Recorded result: 4 tests passed.**

The tests covered:

- Retrieval of passages with metadata.
- Resolution of citations to real passages.
- Answer formatting.
- Abstention when the books lack supporting evidence.

Passing these tests demonstrates that the tested components behaved as expected for the covered cases. It does not establish that every possible answer will be accurate.

## 9. Evaluation Results

The evaluation process uses reference questions, reference answers, and questions that are expected to be unanswerable from the available book collection.

The recorded evaluation results were:

| Metric | Validation | Test |
|---|---:|---:|
| Total questions | 14 | 25 |
| Answerable questions | 7 | 12 |
| Recall@5 hits | 5 | 8 |
| Answers manually reviewed | 5 | 9 |
| Answers marked correct | 3 | 3 |
| Manually reviewed answer accuracy | 60% | 33.3% |
| Questions without answers in the books | 7 | 13 |
| Correctly refused unanswerable questions | 6 | 11 |
| Average response time | 10.7 seconds | 11.8 seconds |

### Interpretation

The retrieval component found at least one expected relevant passage for 5 of 7 answerable validation questions and 8 of 12 answerable test questions.

Manual review marked 3 of 5 validation answers and 3 of 9 test answers as correct. The results show that answer quality remains an area for improvement, even when relevant passages can be retrieved.

The system correctly refused 6 of 7 designated unanswerable validation questions and 11 of 13 designated unanswerable test questions.

These figures describe the recorded evaluation run. They should not be interpreted as a guarantee of performance on every user question. The full evaluation report is available in `evaluation/report.json`.

## 10. Limitations

- The chatbot may generate incomplete or incorrect answers.
- The retrieval system may fail to identify the most relevant passages.
- Citations may not always provide sufficient support for a generated answer.
- The quality of answers depends on the available books, extracted text, metadata, and model capabilities.
- Running the models locally requires sufficient memory, storage, and processing resources.
- Evaluation results are limited to the questions and answers assessed in the recorded run.

## 11. Team Responsibilities

- **Kuunda Banda:** Chatbot development, retrieval implementation, and system integration.
- **Bwalya Musonda:** Book preparation, evaluation, testing, and documentation.

## 12. Responsible Use and Data Management

The book manifest records bibliographic information and the status of book processing or permissions.

Before distributing the project, confirm that the books and associated artifacts are permitted for the intended use. Do not include restricted materials, credentials, or private information in a public submission.

## 13. Conclusion

The Computer Books RAG Chatbot demonstrates how document retrieval and language generation can be combined to answer questions using a collection of computer-related books.

The project implements the main stages of a RAG pipeline, including document processing, semantic retrieval, answer generation, citation handling, and evaluation. Automated tests passed, while the evaluation results identified answer accuracy and evidence support as areas requiring further improvement.
