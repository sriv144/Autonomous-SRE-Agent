from typing import Annotated, List, Dict, Union
from src.agent_core.k8s_client import K8sService

# Global instance for tool use (can be injected dependency in advanced setups)
# Defaulting to local mode false, expecting environment var or config in real app
# For now, we assume this is running where config is available.
try:
    k8s = K8sService(local_mode=False) # Will fail gracefully in tests mock
except:
    k8s = None # Placeholder if initialization fails outside of cluster

def get_pod_logs_tool(
    namespace: Annotated[str, "The Kubernetes namespace of the pod"],
    pod_name: Annotated[str, "The name of the pod to fetch logs from"],
    lines: Annotated[int, "Number of log lines to retrieve"] = 50
) -> str:
    """
    Fetch the logs of a specific pod. Use this to investigate application errors,
    stack traces, or startup failures.
    """
    if not k8s:
        return "Error: K8s client not initialized."
    return k8s.get_pod_logs(namespace, pod_name, lines)

def list_events_tool(
    namespace: Annotated[str, "The Kubernetes namespace to list events from"]
) -> Union[List[Dict], str]:
    """
    List recent events in a namespace. Use this to find cluster-level issues
    like SchedulingFailures, OOMKilled, or ImagePullBackOffs.
    """
    if not k8s:
        return "Error: K8s client not initialized."
    return k8s.get_events(namespace)

def describe_pod_tool(
    namespace: Annotated[str, "The Kubernetes namespace"],
    pod_name: Annotated[str, "The name of the pod"]
) -> Union[Dict, str]:
    """
    Get detailed status information about a pod. Use this to check container
    states, restart counts, and readiness conditions.
    """
    if not k8s:
        return "Error: K8s client not initialized."
    return k8s.describe_pod(namespace, pod_name)
