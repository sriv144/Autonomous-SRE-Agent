import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.api.models import AlertManagerPayload
from src.agent_core.graph import agent_graph
from src.agent_core.slack_notifier import notify_plan_ready, notify_agent_error

router = APIRouter()
logger = logging.getLogger("kubesentient.routes")

async def process_alert(payload: AlertManagerPayload):
    """
    Background task to process the alert using LangGraph.
    On completion, sends the remediation plan (or error) to Slack.
    """
    group_key = payload.groupKey
    logger.info(f"Starting agent for alert group: {group_key}")

    # Extract alert metadata for richer Slack notifications
    alerts_data = payload.model_dump().get("alerts", [])
    alert_names = [
        a.get("labels", {}).get("alertname", "unknown") for a in alerts_data
    ]
    namespace = None
    if alerts_data:
        namespace = alerts_data[0].get("labels", {}).get("namespace")

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

        # Send the remediation plan to Slack
        if plan:
            notify_plan_ready(
                group_key=group_key,
                plan=plan,
                alert_names=alert_names,
                namespace=namespace,
            )
        else:
            logger.warning(f"Agent produced no plan for {group_key} — skipping Slack notification.")

    except Exception as e:
        logger.error(f"Agent failure for {group_key}: {e}")
        # Notify Slack of the failure so the on-call team can investigate manually
        notify_agent_error(group_key=group_key, error=str(e))

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
