"""
Runbook Ingestion Script
========================
Loads all markdown runbooks from the runbooks/ directory into the
Weaviate vector database so the RAG search tool can find them.

Usage (inside Docker container or local venv):
    python -m scripts.ingest_runbooks
    python -m scripts.ingest_runbooks --runbooks-dir ./runbooks
    python -m scripts.ingest_runbooks --runbooks-dir ./runbooks --weaviate-url http://localhost:8080

Environment variables:
    WEAVIATE_URL     - Weaviate HTTP URL (default: http://localhost:8080)
    OPENAI_API_KEY   - Required for text2vec-openai vectorizer in Weaviate
"""

import argparse
import logging
import os
import sys
import time

# Make sure src/ is importable when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ingestion.processor import DocumentProcessor
from src.ingestion.weaviate_client import WeaviateService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("ingest_runbooks")


def wait_for_weaviate(url: str, retries: int = 12, delay: int = 5) -> bool:
    """Poll Weaviate readiness endpoint before ingesting."""
    import urllib.request
    import urllib.error

    ready_url = url.rstrip("/") + "/v1/.well-known/ready"
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(ready_url, timeout=3) as resp:
                if resp.status == 200:
                    logger.info("Weaviate is ready.")
                    return True
        except Exception as e:
            logger.info(f"Waiting for Weaviate ({attempt}/{retries}): {e}")
        time.sleep(delay)
    return False


def main():
    parser = argparse.ArgumentParser(description="Ingest runbooks into Weaviate")
    parser.add_argument(
        "--runbooks-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "runbooks"),
        help="Directory containing .md runbook files (default: ./runbooks)",
    )
    parser.add_argument(
        "--weaviate-url",
        default=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
        help="Weaviate HTTP URL",
    )
    args = parser.parse_args()

    runbooks_dir = os.path.abspath(args.runbooks_dir)
    logger.info(f"Runbooks directory : {runbooks_dir}")
    logger.info(f"Weaviate URL       : {args.weaviate_url}")

    # Validate runbooks directory
    if not os.path.isdir(runbooks_dir):
        logger.error(f"Runbooks directory not found: {runbooks_dir}")
        sys.exit(1)

    md_files = [f for f in os.listdir(runbooks_dir) if f.endswith(".md")]
    if not md_files:
        logger.error(f"No .md files found in {runbooks_dir}")
        sys.exit(1)
    logger.info(f"Found {len(md_files)} runbook(s): {md_files}")

    # Wait for Weaviate to be ready
    if not wait_for_weaviate(args.weaviate_url):
        logger.error("Weaviate did not become ready in time. Aborting.")
        sys.exit(1)

    # Override WEAVIATE_URL for the client
    os.environ["WEAVIATE_URL"] = args.weaviate_url

    # Connect and ensure schema
    weaviate_svc = WeaviateService()
    weaviate_svc.connect()
    weaviate_svc.ensure_schema()

    # Run ingestion
    processor = DocumentProcessor(weaviate_service=weaviate_svc)
    count = processor.run_ingestion(runbooks_dir)

    logger.info(f"Ingestion complete — {count} chunk(s) written to Weaviate.")
    weaviate_svc.close()


if __name__ == "__main__":
    main()
