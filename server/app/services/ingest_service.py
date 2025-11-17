import os
from datetime import datetime, timezone
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore
import weaviate
from dotenv import load_dotenv
from app.utils.logger import get_logger

logger = get_logger()
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://llama3:11434")
EMBED_MODEL_NAME = "nomic-embed-text"  # must match pulled model
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

import os
from datetime import datetime, timezone
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore
import weaviate
from dotenv import load_dotenv
from app.utils.logger import get_logger
from llama_index.core.llms import MockLLM

logger = get_logger()
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://llama3:11434")
EMBED_MODEL_NAME = "nomic-embed-text"
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")


def ingest_document(file_path: str):
    try:
        logger.info(f"Starting ingestion for {file_path}")

        # Configure embeddings (no LLM needed for ingestion)
        Settings.llm = None
        Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL_NAME, base_url=OLLAMA_HOST)
        Settings.text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)

        # Connect to Weaviate
        client = weaviate.Client(WEAVIATE_URL)
        vector_store = WeaviateVectorStore(weaviate_client=client, index_name="Docs")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Load document and annotate
        docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
        logger.info(f"Loaded {len(docs)} chunks from {file_path}")

        for i, d in enumerate(docs):
            d.metadata = {
                "filename": os.path.basename(file_path),
                "ingested_at": datetime.now().isoformat() + "Z"  # RFC3339 format
            }
            logger.info(f"[Doc {i}] Preview: {d.text[:150]}...")

        # Insert into vector DB
        logger.info("Starting vector insertion...")
        index = VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            embed_model=Settings.embed_model
        )
        index.storage_context.persist()  # Force final commit
        logger.info(f"Vector insertion complete for {file_path}")

        # Verify count
        count = client.query.aggregate("Docs").with_meta_count().do()
        logger.info(f"Total objects in 'Docs': {count}")

        return "Ingestion Successful"
    except Exception as e:
        logger.error(f"Ingestion failed for {file_path}: {str(e)}")
        return f"Ingestion Failed: {str(e)}"