from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os

import weaviate

from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from app.services.ingest_service import ingest_document

APP_DIR = Path(__file__).resolve().parent
STORAGE_RAW = APP_DIR / "storage" / "raw"

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://llama3:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2b")

# Configure LLM + Embeddings (Ollama)
Settings.llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=OLLAMA_HOST, request_time=300)

# Initialize Weaviate client (HTTP only)
wclient = weaviate.Client(WEAVIATE_URL)

# Vector store handle
vstore = WeaviateVectorStore(weaviate_client=wclient, index_name="Docs")

app = FastAPI(title="Company Knowledge Chatbot API", version="0.1.0")

# CORS for dev; tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/health")
def health():
    # Quick checks
    try:
        _ = wclient.is_ready()
        w_ok = True
    except Exception:
        w_ok = False
    return {
        "status": "ok",
        "weaviate_ready": w_ok,
        "ollama_host": OLLAMA_HOST,
        "model": OLLAMA_MODEL,
    }

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    STORAGE_RAW.mkdir(parents=True, exist_ok=True)
    dest = STORAGE_RAW / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # # Read all docs in storage/raw (simple for now)
    # docs = SimpleDirectoryReader(input_dir=str(STORAGE_RAW)).load_data()

    # # Build/append index into Weaviate
    # index = VectorStoreIndex.from_documents(docs, vector_store=vstore)
    result = ingest_document(str(dest))
    return {"message": f"Ingested {len(result)} documents", "file_saved": str(dest.name)}

@app.post("/query")
async def query(payload: dict):
    q = payload.get("q")
    if not q:
        raise HTTPException(status_code=400, detail="Missing field 'q'")
    try:
        index = VectorStoreIndex.from_vector_store(vstore)
        engine = index.as_query_engine(similarity_top_k=5)
        ans = engine.query(q)
        return {"answer": str(ans), "source_nodes": [n.node_id for n in ans.source_nodes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")