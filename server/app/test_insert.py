# import weaviate
# import os
# from datetime import datetime, timezone

# WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")

# client = weaviate.Client(WEAVIATE_URL)

# print("Schema:", client.schema.get())

# data_object = {
#     "text": "Hello, this is a test entry.",
#     "filename": "manual_insert.txt",
#     "ingested_at": datetime.now(timezone.utc).isoformat()  # <-- FIXED
# }

# client.data_object.create(data_object, class_name="Docs")
# print("Manual insertion complete.")

# result = client.query.get("Docs", ["text", "filename", "ingested_at"]).do()
# print("Query result:", result)

# from llama_index.embeddings.ollama import OllamaEmbedding

# embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://llama3:11434")
# print(embed_model.get_text_embedding("Test embedding"))

# import weaviate, os
# from llama_index.embeddings.ollama import OllamaEmbedding
# from datetime import datetime

# WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
# client = weaviate.Client(WEAVIATE_URL)

# embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://llama3:11434")
# vector = embed_model.get_text_embedding("This is a test document")

# client.data_object.create(
#     {
#         "text": "This is a test document",
#         "filename": "test_doc.txt",
#         "ingested_at": datetime.utcnow().isoformat() + "Z"
#     },
#     class_name="Docs",
#     vector=vector
# )

# print(client.query.get("Docs", ["text", "filename"]).do())

from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms import OpenAI  # or Ollama, depending on your setup

# Setup LLM for rewriting answers (human-readable)
llm = OpenAI(model="gpt-4", temperature=0.3)  # replace with your LLM
service_context = ServiceContext.from_defaults(llm=llm)

# Wrap your retriever (Weaviate vector store)
index = VectorStoreIndex.from_vector_store(weaviate_vector_store, service_context=service_context)
retriever = index.as_retriever()

# Build a query engine with post-processing
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    service_context=service_context,
    response_synthesizer="compact"  # forces clean human-friendly summary
)

def ask_human_friendly(query: str) -> str:
    raw_response = query_engine.query(query)
    
    # Add an explicit instruction to rephrase nicely for humans
    friendly_response = llm.complete(
        f"""
        Rewrite the following context into a clear, human-readable answer,
        suitable for an employee asking an HR question.

        Context:
        {raw_response}

        Answer:
        """
    )
    return friendly_response.text


# Example
print(ask_human_friendly("What is the Provident Fund Policy?"))
