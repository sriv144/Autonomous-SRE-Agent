from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from src.api.models import AlertManagerPayload

class AgentState(TypedDict):
    """
    Represents the state of the SRE agent during an investigation.
    """
    # Chat history for the LLM
    messages: List[BaseMessage]
    
    # The initial alert payload triggering this run
    alert_payload: Optional[Dict[str, Any]]
    
    # Structured knowledge gathered during investigation
    # e.g., {"logs": "...", "events": "..."}
    context: Dict[str, Any]
    
    # The proposed plan for remediation
    plan: Optional[str]
    
    # Status flags
    investigation_complete: bool
    requires_approval: bool
