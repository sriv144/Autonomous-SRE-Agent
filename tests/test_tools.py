import pytest
from unittest.mock import MagicMock, patch
from src.agent_core.k8s_client import K8sService

# Mock kubernetes config before importing the actual module to avoid load errors
with patch("kubernetes.config.load_incluster_config"), \
     patch("kubernetes.config.load_kube_config"):
    from src.agent_core.tools import get_pod_logs_tool, list_events_tool, describe_pod_tool

@pytest.fixture
def mock_k8s_service():
    with patch("src.agent_core.tools.k8s") as mock_service:
        yield mock_service

def test_get_pod_logs_tool(mock_k8s_service):
    mock_k8s_service.get_pod_logs.return_value = "Log line 1\nLog line 2"
    
    logs = get_pod_logs_tool("default", "test-pod-1")
    
    mock_k8s_service.get_pod_logs.assert_called_once_with("default", "test-pod-1", 50)
    assert logs == "Log line 1\nLog line 2"

def test_list_events_tool(mock_k8s_service):
    mock_events = [{"type": "Warning", "message": "OOMKilled"}]
    mock_k8s_service.get_events.return_value = mock_events
    
    result = list_events_tool("default")
    
    mock_k8s_service.get_events.assert_called_once_with("default")
    assert result == mock_events

def test_describe_pod_tool(mock_k8s_service):
    mock_desc = {"phase": "Running", "restart_count": 0}
    mock_k8s_service.describe_pod.return_value = mock_desc
    
    result = describe_pod_tool("default", "test-pod-1")
    
    mock_k8s_service.describe_pod.assert_called_once_with("default", "test-pod-1")
    assert result == mock_desc
