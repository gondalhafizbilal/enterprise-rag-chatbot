import os
import weaviate

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

client = weaviate.Client(WEAVIATE_URL)

schema = {
    "classes": [
        {
            "class": "Docs",
            "description": "Document text and metadata",
            "properties": [
                {"name": "text", "dataType": ["text"]},
                {"name": "filename", "dataType": ["text"]},
                {"name": "ingested_at", "dataType": ["date"]},
            ],
        }
    ]
}

# Fetch current schema
current_schema = client.schema.get()

# Only create if class does not exist
existing_classes = [cls["class"] for cls in current_schema.get("classes", [])]
if "Docs" not in existing_classes:
    client.schema.create_class(schema["classes"][0])
    print("Schema created successfully.")
else:
    print("Schema already exists. Skipping creation.")
