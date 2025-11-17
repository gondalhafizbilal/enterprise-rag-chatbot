# 📚 Enterprise Rag Chatbot

A FastAPI-based service that ingests documents into **Weaviate**, indexes them with **LlamaIndex**, and lets you query them with semantic search.  
By default, the backend returns human-readable document chunks from Weaviate.  
Optionally, you can enable **Ollama** to summarize or generate natural answers.

---

## 🚀 Features

- Upload and ingest documents (`/ingest` endpoint).
- Store embeddings in **Weaviate** (vector database).
- Query stored documents with semantic similarity (`/query` endpoint).
- Pluggable LLM backend (**Ollama**) for natural language summarization.
- Lightweight REST API using **FastAPI**.
- Docker-compose ready for local development.

---

## 🛠️ Tech Stack

- **FastAPI** → REST API backend
- **Weaviate** → Vector database for embeddings
- **LlamaIndex** → Data ingestion & query pipeline
- **Ollama** (optional) → Local LLM for summarization
- **Docker Compose** → One-command environment setup

---

## 📂 Project Structure

```
.
├── app.py                # FastAPI backend
├── ingest_service.py     # (Optional) Ingestion helpers
├── storage/
│   └── raw/              # Uploaded files are saved here
├── docker-compose.yml    # Orchestration of Weaviate + Ollama + API
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## ⚡ Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/gondalhafizbilal/enterprise-rag-chatbot.git
cd enterprise-rag-chatbot
```

### 2. Start services with Docker Compose

```bash
docker compose up -d
```

This will start:

- `weaviate` at `http://localhost:8080`
- `ollama` at `http://localhost:11434` (if enabled)
- `fastapi` backend at `http://localhost:8000`

### 3. Install Python dependencies (for local dev)

```bash
pip install -r requirements.txt
```

---

## 📥 Ingest Documents

Upload a document (PDF, text, etc.):

```bash
curl -X POST "http://localhost:8000/ingest"   -F "file=@manual-test-001.pdf"
```

The file is stored in `storage/raw/` and indexed into Weaviate.

---

## 🔍 Query the Knowledge Base

Ask a question about your documents:

```bash
curl -X POST "http://localhost:8000/query"   -H "Content-Type: application/json"   -d '{"q": "What is the refund policy?"}'
```

Response:

```json
{
  "answer": "The refund policy states that customers can request a refund within 30 days...",
  "source_nodes": ["a4f6773d-5c58-46a3-ac57-b130816f9bc1"]
}
```

---

## 🧠 Human-Readable Mode vs LLM Mode

- **Default mode** → returns retrieved chunks directly (no LLM). ✅ Fast & reliable.
- **LLM mode** (optional) → summarize into a natural answer using Ollama.

Switch mode by editing `/query`:

```python
engine = index.as_query_engine(similarity_top_k=5)  # LLM mode (can timeout if Ollama is slow)
```

---

## 🧪 Health Check

Check if services are running:

```bash
curl http://localhost:8000/health
```

Example:

```json
{
  "status": "ok",
  "weaviate_ready": true,
  "ollama_host": "http://llama3:11434",
  "model": "llama3"
}
```

---

## 🗑️ Reset Index

To clear everything:

```bash
docker compose down -v
```

---

## 🔮 Roadmap

- ✅ Ingest + query basic documents
- ✅ Support for Weaviate vector DB
- ⬜️ LLM summarization toggle (switch between human-readable + generated answers)
- ⬜️ Frontend UI (React-based chat interface)
- ⬜️ Authentication for production use

---

## 📝 License

MIT License.  
Feel free to use, modify, and share.
