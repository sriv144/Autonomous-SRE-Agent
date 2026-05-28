import os
from typing import Annotated, List, Dict, Union
from src.agent_core.k8s_client import K8sService


def _resolve_local_mode() -> bool:
    """Whether to load a local kubeconfig (dev) instead of in-cluster config (prod).

    Controlled by the ``K8S_LOCAL_MODE`` environment variable so the same image
    can target a developer's kubeconfig or an in-cluster ServiceAccount without
    editing source. Defaults to in-cluster (False) to preserve prior behavior.
    """
    return os.getenv("K8S_LOCAL_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}


# Global instance for tool use (can be injected as a dependency in advanced setups).
# Initialization may fail outside a cluster (or without a kubeconfig); in that case
# the tools below degrade gracefully to an error string instead of crashing import.
try:
    k8s = K8sService(local_mode=_resolve_local_mode())  # Will fail gracefully in tests/mocks
except Exception:
    k8s = None  # Placeholder if initialization fails outside of cluster

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
