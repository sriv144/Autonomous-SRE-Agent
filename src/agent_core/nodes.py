import logging
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from src.agent_core.state import AgentState
from src.agent_core.tools import get_pod_logs_tool, list_events_tool, describe_pod_tool
from src.agent_core.rag_tool import search_runbooks_tool

logger = logging.getLogger("kubesentient.agent")

# Default models per provider. Anthropic default is Sonnet 4.6 — strong
# reasoning, cost-effective for an SRE remediation loop. Override per
# deployment with ANTHROPIC_MODEL / OPENAI_MODEL.
_DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
_DEFAULT_OPENAI_MODEL = "gpt-4-turbo-preview"


def _build_llm():
    """Build the LangChain chat model based on LLM_PROVIDER.

    LLM_PROVIDER=openai     -> ChatOpenAI (default, preserves prior behavior)
    LLM_PROVIDER=anthropic  -> ChatAnthropic (Claude Sonnet 4.6 by default)
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:  # pragma: no cover - import-time guard
            raise ImportError(
                "LLM_PROVIDER=anthropic requires the langchain-anthropic "
                "package. Install it with: pip install langchain-anthropic"
            ) from exc
        model = os.getenv("ANTHROPIC_MODEL", _DEFAULT_ANTHROPIC_MODEL)
        logger.info("Initializing Anthropic LLM provider model=%s", model)
        return ChatAnthropic(model=model, temperature=0)

    model = os.getenv("OPENAI_MODEL", _DEFAULT_OPENAI_MODEL)
    logger.info("Initializing OpenAI LLM provider model=%s", model)
    return ChatOpenAI(model=model, temperature=0)


# Initialize LLM
llm = _build_llm()

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
