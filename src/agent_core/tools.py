import logging
import os
from typing import Annotated, Dict, List, Union

from src.agent_core.k8s_client import K8sService

logger = logging.getLogger("kubesentient.tools")

# Local-mode toggle. Defaults to False so the deployed pod keeps its existing
# in-cluster behaviour. Set KUBESENTIENT_LOCAL_MODE=true (or 1, yes, on) for
# local dev so the kubeconfig at ~/.kube/config is used instead.
_LOCAL_MODE_ENV = os.getenv("KUBESENTIENT_LOCAL_MODE", "false").strip().lower()
_LOCAL_MODE = _LOCAL_MODE_ENV in {"1", "true", "yes", "on"}

try:
    k8s = K8sService(local_mode=_LOCAL_MODE)
except Exception as exc:  # noqa: BLE001 - mocked tests construct without a cluster
    logger.warning(
        "K8s client init failed (local_mode=%s): %s. "
        "Tools will return a graceful 'not initialized' error string.",
        _LOCAL_MODE,
        exc,
    )
    k8s = None


def get_pod_logs_tool(
    namespace: Annotated[str, "The Kubernetes namespace of the pod"],
    pod_name: Annotated[str, "The name of the pod to fetch logs from"],
    lines: Annotated[int, "Number of log lines to retrieve"] = 50,
) -> str:
    """
    Fetch the logs of a specific pod. Use this to investigate application errors,
    stack traces, or startup failures.
    """
    if not k8s:
        return "Error: K8s client not initialized."
    return k8s.get_pod_logs(namespace, pod_name, lines)


def list_events_tool(
    namespace: Annotated[str, "The Kubernetes namespace to list events from"],
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
    pod_name: Annotated[str, "The name of the pod"],
) -> Union[Dict, str]:
    """
    Get detailed status information about a pod. Use this to check container
    states, restart counts, and readiness conditions.
    """
    if not k8s:
        return "Error: K8s client not initialized."
    return k8s.describe_pod(namespace, pod_name)
