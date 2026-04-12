import pytest
from unittest.mock import MagicMock, patch
from src.ingestion.weaviate_client import WeaviateService
from src.agent_core.rag_tool import search_runbooks_tool

@pytest.fixture
def mock_weaviate_service():
    with patch("src.agent_core.rag_tool.rag_service") as mock_service:
        yield mock_service

def test_search_runbooks_tool_success(mock_weaviate_service):
    """Test successful search returns formatted string."""
    mock_results = [
        {"title": "OOM-Guide.md (Part 1)", "content": "Check memory limits."}
    ]
    mock_weaviate_service.search.return_value = mock_results
    
    result = search_runbooks_tool("memory issue")
    
    mock_weaviate_service.search.assert_called_once_with("memory issue", limit=3)
    assert "Found relevant runbooks" in result
    assert "Check memory limits" in result

def test_search_runbooks_tool_empty(mock_weaviate_service):
    """Test empty results."""
    mock_weaviate_service.search.return_value = []
    
    result = search_runbooks_tool("unknown error")
    
    assert result == "No relevant runbooks found."

def test_search_runbooks_tool_error(mock_weaviate_service):
    """Test error handling."""
    mock_weaviate_service.search.side_effect = Exception("Connection failed")
    
    result = search_runbooks_tool("query")
    
    assert "Error searching runbooks" in result
    assert "Connection failed" in result

@patch("src.ingestion.processor.glob.glob")
@patch("builtins.open", new_callable=MagicMock)
def test_document_processor_chunking(mock_file, mock_glob):
    """Test that text is correctly chunked."""
    from src.ingestion.processor import DocumentProcessor
    
    # Setup mocks
    mock_glob.return_value = ["/docs/runbook.md"]
    mock_file_handle = MagicMock()
    mock_file_handle.read.return_value = "A" * 1500 # 1500 chars
    mock_file.return_value.__enter__.return_value = mock_file_handle
    
    mock_weaviate = MagicMock()
    processor = DocumentProcessor(mock_weaviate)
    
    # Execute
    chunks = processor.load_and_chunk("/docs")
    
    # Verify: 1500 chars, chunk_size=1000, overlap=100
    # Chunk 1: 0-1000
    # Chunk 2: 900-1900 (truncated to 1500)
    # Expected: 2 chunks
    assert len(chunks) == 2
    assert len(chunks[0]["content"]) == 1000
    assert chunks[0]["title"] == "runbook.md (Part 1)"
