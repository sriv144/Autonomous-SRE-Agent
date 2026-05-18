import logging
import json
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from src.agent_core.state import AgentState
from src.agent_core.tools import get_pod_logs_tool, list_events_tool, describe_pod_tool
from src.agent_core.rag_tool import search_runbooks_tool

logger = logging.getLogger("kubesentient.agent")

# Anthropic Claude is the reasoning engine for the investigator + planner
# nodes. Sonnet 4.6 is fast enough for an interactive tool-use loop and
# still strong at multi-step structured reasoning.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

llm = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)

# Bind tools to the LLM
tools = [get_pod_logs_tool, list_events_tool, describe_pod_tool, search_runbooks_tool]
llm_with_tools = llm.bind_tools(tools)


def initial_triage(state: AgentState):
    """Analyzes the alert payload and sets the initial context."""
    logger.info("Node: initial_triage")
    alert = state.get("alert_payload", {})

    alerts_summary = json.dumps(alert.get("alerts", []), indent=2)
    group_key = alert.get("groupKey", "Unknown")

    msg = f"""
    Received Alert Group: {group_key}
    Alerts:
    {alerts_summary}

    Please investigate the affected resources using your tools.
    Check logs, events, and describe the pods.
    Also search for runbooks if the issue isn't obvious.
    """

    return {
        "messages": [
            SystemMessage(content="You are KubeSentient, an autonomous SRE."),
            HumanMessage(content=msg),
        ],
        "context": {"group_key": group_key},
        "investigation_complete": False,
    }


def investigator(state: AgentState):
    """The core loop where the agent calls tools to gather info."""
    logger.info("Node: investigator")
    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    if not response.tool_calls:
        return {
            "messages": [response],
            "investigation_complete": True,
        }

    return {"messages": [response]}


# Prebuilt tool execution node from LangGraph
tool_node = ToolNode(tools)


def planner(state: AgentState):
    """Synthesizes findings into a remediation plan."""
    logger.info("Node: planner")
    messages = state["messages"]

    prompt = """
    Based on the investigation above, please formulate a detailed remediation plan.

    1. Summarize the Root Cause.
    2. Propose specific kubectl commands or actions to fix it.
    3. State if human intervention is critical.

    Format the output as a Markdown report.
    """

    response = llm.invoke(messages + [HumanMessage(content=prompt)])

    return {
        "messages": [response],
        "plan": response.content,
        "requires_approval": True,
    }


def human_approval(state: AgentState):
    """A dummy node that acts as a breakpoint in the graph.

    In a real app, this would suspend execution until an API call resumes it.
    """
    logger.info("Node: human_approval - Waiting for user signal (Mocked)")
    return {}
