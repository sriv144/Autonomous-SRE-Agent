import logging
import json
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from src.agent_core.state import AgentState
from src.agent_core.tools import get_pod_logs_tool, list_events_tool, describe_pod_tool
from src.agent_core.rag_tool import search_runbooks_tool
from src.agent_core.llm_provider import build_llm

logger = logging.getLogger("kubesentient.agent")

# Initialize LLM via provider factory.
# Default is OpenAI gpt-4-turbo-preview. Set LLM_PROVIDER=anthropic to use Claude.
llm = build_llm()

# Bind tools to the LLM
tools = [get_pod_logs_tool, list_events_tool, describe_pod_tool, search_runbooks_tool]
llm_with_tools = llm.bind_tools(tools)

def initial_triage(state: AgentState):
    """
    Analyzes the alert payload and sets the initial context.
    """
    logger.info("Node: initial_triage")
    alert = state.get("alert_payload", {})
    
    # Extract key info to prime the LLM
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
        "messages": [SystemMessage(content="You are KubeSentient, an autonomous SRE."), HumanMessage(content=msg)],
        "context": {"group_key": group_key},
        "investigation_complete": False
    }

def investigator(state: AgentState):
    """
    The core loop where the agent calls tools to gather info.
    """
    logger.info("Node: investigator")
    messages = state["messages"]
    
    # Invoke LLM
    response = llm_with_tools.invoke(messages)
    
    # If the LLM doesn't want to call any more tools, we assume investigation is done
    if not response.tool_calls:
        return {
            "messages": [response],
            "investigation_complete": True
        }
    
    return {"messages": [response]}

# Prebuilt tool execution node from LangGraph
tool_node = ToolNode(tools)

def planner(state: AgentState):
    """
    Synthesizes findings into a remediation plan.
    """
    logger.info("Node: planner")
    messages = state["messages"]
    
    prompt = """
    Based on the investigation above, please formulate a detailed remediation plan.
    
    1. Summarize the Root Cause.
    2. Propose specific kubectl commands or actions to fix it.
    3. State if human intervention is critical.
    
    Format the output as a Markdown report.
    """
    
    # We use a standard generation call here, not tool binding
    response = llm.invoke(messages + [HumanMessage(content=prompt)])
    
    return {
        "messages": [response],
        "plan": response.content,
        "requires_approval": True
    }

def human_approval(state: AgentState):
    """
    A dummy node that acts as a breakpoint in the graph.
    In a real app, this would suspend execution until an API call resumes it.
    """
    logger.info("Node: human_approval - Waiting for user signal (Mocked)")
    # For now, we just pass through or stop.
    # In LangGraph, we use 'interrupt_before' on this node.
    return {}
