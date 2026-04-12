from typing import Annotated
from src.ingestion.weaviate_client import WeaviateService

# Global instance
# In a real app, this would be initialized with connection checks
rag_service = WeaviateService()

def search_runbooks_tool(
    query: Annotated[str, "The search query to find relevant runbooks or documentation"]
) -> str:
    """
    Search the internal runbook knowledge base for solutions, known issues, or
    troubleshooting guides. Use this when you are investigating an alert and
    need context on how to resolve it.
    """
    try:
        results = rag_service.search(query, limit=3)
        if not results:
            return "No relevant runbooks found."
        
        formatted_results = "Found relevant runbooks:\n\n"
        for i, res in enumerate(results):
            formatted_results += f"Source: {res['title']}\n"
            formatted_results += f"Content: {res['content']}\n"
            formatted_results += "---\n"
            
        return formatted_results
    except Exception as e:
        return f"Error searching runbooks: {str(e)}"
