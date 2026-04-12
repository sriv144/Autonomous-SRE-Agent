import os
import glob
from typing import List, Dict
from src.ingestion.weaviate_client import WeaviateService

class DocumentProcessor:
    """
    Handles loading markdown runbooks, chunking them, and ingesting into Weaviate.
    """
    def __init__(self, weaviate_service: WeaviateService):
        self.weaviate = weaviate_service

    def load_and_chunk(self, directory_path: str) -> List[Dict[str, str]]:
        """
        Recursively finds .md files, reads them, and splits them into chunks.
        """
        chunks = []
        files = glob.glob(os.path.join(directory_path, "**/*.md"), recursive=True)
        
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_name = os.path.basename(file_path)
                
                # Naive chunking by paragraphs or fixed size
                # For code-heavy runbooks, splitting by headers is better, 
                # but we'll use a simple overlap strategy here.
                # 1000 chars ~ 200-300 tokens
                text_chunks = self._chunk_text(content, chunk_size=1000, overlap=100)
                
                for i, chunk in enumerate(text_chunks):
                    chunks.append({
                        "content": chunk,
                        "title": f"{file_name} (Part {i+1})",
                        "source": file_path
                    })
        return chunks

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def run_ingestion(self, directory_path: str) -> int:
        """Main entry point to run the ingestion pipeline. Returns number of chunks ingested."""
        self.weaviate.ensure_schema()
        chunks = self.load_and_chunk(directory_path)
        print(f"Found {len(chunks)} chunks to ingest...")

        for chunk in chunks:
            self.weaviate.ingest_chunk(
                content=chunk["content"],
                title=chunk["title"],
                source=chunk["source"]
            )
        print("Ingestion complete.")
        return len(chunks)
