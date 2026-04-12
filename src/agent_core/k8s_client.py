import logging
from typing import Optional, List, Dict, Any
from kubernetes import client, config

logger = logging.getLogger("kubesentient.k8s")

class K8sService:
    """
    Wrapper around kubernetes-python client to provide safe, simplified access
    for the AI agent. Enforces read-only operations where possible by design.
    """
    def __init__(self, local_mode: bool = False):
        try:
            if local_mode:
                config.load_kube_config()
                logger.info("Loaded local kubeconfig")
            else:
                config.load_incluster_config()
                logger.info("Loaded in-cluster config")
            
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
        except Exception as e:
            logger.error(f"Failed to initialize K8s client: {e}")
            raise

    def get_pod_logs(self, namespace: str, pod_name: str, lines: int = 50) -> str:
        """Retrieves the last N lines of logs from a pod."""
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=lines
            )
            return logs
        except client.ApiException as e:
            return f"Error retrieving logs for {pod_name}: {e.reason}"

    def get_events(self, namespace: str) -> List[Dict[str, Any]]:
        """List events in the namespace to identify issues."""
        try:
            events = self.core_v1.list_namespaced_event(namespace=namespace)
            return [
                {
                    "type": e.type,
                    "reason": e.reason,
                    "message": e.message,
                    "object": e.involved_object.name,
                    "timestamp": e.last_timestamp or e.event_time
                }
                for e in events.items
            ]
        except client.ApiException as e:
            logger.error(f"Error listing events: {e}")
            return []

    def describe_pod(self, namespace: str, pod_name: str) -> Dict[str, Any]:
        """Get detailed status of a pod."""
        try:
            pod = self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            return {
                "phase": pod.status.phase,
                "conditions": [
                    {"type": c.type, "status": c.status, "message": c.message} 
                    for c in (pod.status.conditions or [])
                ],
                "container_statuses": [
                     {
                         "name": cs.name,
                         "restart_count": cs.restart_count,
                         "state": list(cs.state.to_dict().keys())[0] if cs.state else "unknown"
                     }
                     for cs in (pod.status.container_statuses or [])
                ]
            }
        except client.ApiException as e:
            return {"error": f"Failed to describe pod {pod_name}: {e.reason}"}
