from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Alert(BaseModel):
    """Schema for a single alert within the webhook payload."""
    status: str = Field(..., description="Status of the alert (firing, resolved)")
    labels: Dict[str, str] = Field(..., description="Key-value pairs identifying the alert instance")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Info fields (summary, description, runbook_url)")
    startsAt: datetime
    endsAt: Optional[datetime] = None
    generatorURL: Optional[str] = None
    fingerprint: Optional[str] = None

class AlertManagerPayload(BaseModel):
    """Schema for the incoming webhook from AlertManager."""
    version: str = Field(..., description="Protocol version")
    groupKey: str
    truncatedAlerts: int = 0
    status: str = Field(..., description="Overall status (firing, resolved)")
    receiver: str
    groupLabels: Dict[str, str]
    commonLabels: Dict[str, str]
    commonAnnotations: Dict[str, str]
    externalURL: str
    alerts: List[Alert]

    class Config:
        json_schema_extra = {
            "example": {
                "version": "4",
                "groupKey": "{}:{alertname=\"HighMemory\"}",
                "status": "firing",
                "receiver": "webhook",
                "groupLabels": {"alertname": "HighMemory"},
                "commonLabels": {"severity": "critical"},
                "commonAnnotations": {"summary": "High memory usage"},
                "externalURL": "http://alertmanager:9093",
                "alerts": [
                    {
                        "status": "firing",
                        "labels": {"alertname": "HighMemory", "instance": "server1"},
                        "annotations": {"description": "Memory usage > 90%"},
                        "startsAt": "2023-01-01T10:00:00Z",
                        "endsAt": "0001-01-01T00:00:00Z"
                    }
                ]
            }
        }
