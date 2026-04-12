from langgraph.graph import StateGraph, END
from src.agent_core.state import AgentState
from src.agent_core.nodes import initial_triage, investigator, tool_node, planner, human_approval

def should_continue_investigation(state: AgentState):
    """
    Conditional edge logic.
    If the last message was a tool call (managed by investigator logic mostly), 
    or if investigation is not marked complete.
    
    Actually, with the `investigator` node structure:
    - If LLM returned tool_calls, `investigation_complete` is NOT set (implicit).
    - If LLM returned text, `investigation_complete` IS set to True.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, we MUST go to the tool node
    if last_message.tool_calls:
        return "tools"
    
    # Otherwise, we proceed to planning
    return "planner"

def build_graph():
    """
    Constructs the KubeSentient agent graph.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("triage", initial_triage)
    workflow.add_node("investigator", investigator)
    workflow.add_node("tools", tool_node)
    workflow.add_node("planner", planner)
    workflow.add_node("approval", human_approval)
    
    # Set Entry Point
    workflow.set_entry_point("triage")
    
    # Edges
    workflow.add_edge("triage", "investigator")
    
    # Conditional Edge from Investigator
    workflow.add_conditional_edges(
        "investigator",
        should_continue_investigation,
        {
            "tools": "tools",
            "planner": "planner"
        }
    )
    
    # From tools, go back to investigator to process results
    workflow.add_edge("tools", "investigator")
    
    # From planner, go to approval
    workflow.add_edge("planner", "approval")
    
    # End after approval (for this scaffold)
    workflow.add_edge("approval", END)
    
    # Compile
    # Memory checkpointer would go here for persistence
    app = workflow.compile()
    
    return app

# Process instance
agent_graph = build_graph()
