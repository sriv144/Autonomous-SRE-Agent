import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.api.models import AlertManagerPayload
from src.agent_core.graph import agent_graph

router = APIRouter()
logger = logging.getLogger("kubesentient.routes")

async def process_alert(payload: AlertManagerPayload):
    """
    Background task to process the alert using LangGraph.
    """
    group_key = payload.groupKey
    logger.info(f"Starting agent for alert group: {group_key}")
    
    # Inputs for the graph
    initial_state = {
        "alert_payload": payload.model_dump(),
        "messages": [],
        "context": {},
        "investigation_complete": False,
        "requires_approval": False,
        "plan": None
    }
    
    try:
        # Run the graph
        # config={"recursion_limit": 20}
        result = await agent_graph.ainvoke(initial_state)
        
        plan = result.get("plan")
        logger.info(f"Agent finished. Remediation Plan:\n{plan}")
        
        # Here we would send the plan to Slack using 'result' content
        
    except Exception as e:
        logger.error(f"Agent failure for {group_key}: {e}")

@router.post("/alerts", status_code=202)
async def receive_alerts(payload: AlertManagerPayload, background_tasks: BackgroundTasks):
    """
    Endpoint to receive webhooks from Prometheus AlertManager.
    """
    try:
        logger.info(f"Received webhook from {payload.receiver} with {len(payload.alerts)} alerts")
        background_tasks.add_task(process_alert, payload)
        return {"status": "accepted", "message": "Alerts queued for processing"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")
