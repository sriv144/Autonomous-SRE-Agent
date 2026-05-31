import json
import logging
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from src.agent_core.rag_tool import search_runbooks_tool
from src.agent_core.state import AgentState
from src.agent_core.tools import describe_pod_tool, get_pod_logs_tool, list_events_tool

logger = logging.getLogger("kubesentient.agent")

# Anthropic Claude powers reasoning. Sonnet is the default; override with
# ANTHROPIC_MODEL (e.g. claude-opus-4-8) for harder incidents.
_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
llm = ChatAnthropic(model=_MODEL, temperature=0, max_tokens=4096)

tools = [get_pod_logs_tool, list_events_tool, describe_pod_tool, search_runbooks_tool]
llm_with_tools = llm.bind_tools(tools)


def initial_triage(state: AgentState):
    """Analyze the alert payload and set the initial context."""
    logger.info("Node: initial_triage")
    alert = state.get("alert_payload", {})

    alerts_summary = json.dumps(alert.get("alerts", []), indent=2)
    group_key = alert.get("groupKey", "Unknown")

    msg = (
        f"Received Alert Group: {group_key}\n"
        f"Alerts:\n{alerts_summary}\n\n"
        "Please investigate the affected resources using your tools. "
        "Check logs, events, and describe the pods. "
        "Also search for runbooks if the issue isn't obvious."
    )

    return {
        "messages": [
            SystemMessage(content="You are KubeSentient, an autonomous SRE."),
            HumanMessage(content=msg),
        ],
        "context": {"group_key": group_key},
        "investigation_complete": False,
    }


def investigator(state: AgentState):
    """Core loop where the agent calls tools to gather info."""
    logger.info("Node: investigator")
    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        return {
            "messages": [response],
            "investigation_complete": True,
        }

    return {"messages": [response]}


tool_node = ToolNode(tools)


def planner(state: AgentState):
    """Synthesize findings into a remediation plan."""
    logger.info("Node: planner")
    messages = state["messages"]

    prompt = (
        "Based on the investigation above, please formulate a detailed remediation plan.\n\n"
        "1. Summarize the Root Cause.\n"
        "2. Propose specific kubectl commands or actions to fix it.\n"
        "3. State if human intervention is critical.\n\n"
        "Format the output as a Markdown report."
    )

    response = llm.invoke(messages + [HumanMessage(content=prompt)])

    return {
        "messages": [response],
        "plan": response.content,
        "requires_approval": True,
    }


def human_approval(state: AgentState):
    """Dummy node acting as a breakpoint in the graph."""
    logger.info("Node: human_approval - Waiting for user signal (Mocked)")
    return {}
