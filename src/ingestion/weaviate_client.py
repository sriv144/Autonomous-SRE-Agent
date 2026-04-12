import logging
import os
import weaviate
import weaviate.classes.config as wvc
from typing import List, Dict, Any

logger = logging.getLogger("kubesentient.weaviate")

class WeaviateService:
    """
    Wrapper for Weaviate Vector DB (v4 client).
    Handles schema initialization and vector searches.
    """
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.client = None
        self._collection_name = "Runbook"

    def connect(self):
        """Explicit connection management."""
        if not self.client:
            # parsing host and port from URL for v4 connect_to_custom if needed
            # For simplicity in K8s, we might pass the direct internal URL.
            # v4 often prefers headers and grpc.
            # Fallback to legacy-style simple init for v4 compat layer if complex
            # or use connect_to_local if running in same pod (not case here).
            # We will use connect_to_custom.
            
            # Simplified connection for demo purposes (assuming no auth)
            host = self.url.replace("http://", "").split(":")[0]
            port = int(self.url.split(":")[-1])
            
            try:
                self.client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=False,
                    grpc_host=host,
                    grpc_port=50051, # Default gRPC port
                    grpc_secure=False
                )
                logger.info("Connected to Weaviate")
            except Exception as e:
                logger.error(f"Failed to connect to Weaviate: {e}")
                # Don't raise immediately to allow offline mode/mocking in tests
    
    def ensure_schema(self):
        """Ensures the Runbook collection exists."""
        if not self.client:
            self.connect()
        
        try:
            if not self.client.collections.exists(self._collection_name):
                self.client.collections.create(
                    name=self._collection_name,
                    properties=[
                        wvc.Property(name="content", data_type=wvc.DataType.TEXT),
                        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
                        wvc.Property(name="source", data_type=wvc.DataType.TEXT),
                    ],
                    # Using default vectorizer (none) if no OpenAI key, 
                    # or 'text2vec-openai' if configured in Weaviate sidecar.
                    # For this demo, we assume the Weaviate instance is configured.
                )
                logger.info(f"Created collection {self._collection_name}")
        except Exception as e:
            logger.error(f"Schema check failed: {e}")

    def ingest_chunk(self, content: str, title: str, source: str):
        """Ingests a single chunk of text."""
        if not self.client:
            self.connect()
            
        collection = self.client.collections.get(self._collection_name)
        collection.data.insert({
            "content": content,
            "title": title,
            "source": source
        })

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Performs a near-text search."""
        if not self.client:
            self.connect()
            
        collection = self.client.collections.get(self._collection_name)
        # Note: near_text requires a vectorizer module enabled in Weaviate
        response = collection.query.near_text(
            query=query,
            limit=limit
        )
        
        results = []
        for obj in response.objects:
            results.append({
                "content": obj.properties["content"],
                "title": obj.properties["title"]
            })
        return results

    def close(self):
        if self.client:
            self.client.close()
