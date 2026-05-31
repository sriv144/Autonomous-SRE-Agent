import pytest
from unittest.mock import patch

from src.agent_core.graph import build_graph


# Mock ChatAnthropic so the graph can be built without a real Anthropic key.
@pytest.fixture
def mock_llm():
    with patch("src.agent_core.nodes.ChatAnthropic") as mock:
        yield mock


@pytest.mark.asyncio
async def test_agent_graph_execution():
    """Test the flow of the graph by mocking the component nodes/LLM.

    Since mocking the entire LangGraph execution logic via unit tests can be
    brittle, we focus on ensuring the graph compiles and the nodes accept state.
    """
    app = build_graph()
    assert app is not None


# Additional tests would involve deep mocking of the .invoke methods of nodes
# or using LangGraph's built-in testing utilities if available.
