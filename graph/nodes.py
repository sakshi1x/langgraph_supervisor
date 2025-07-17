"""
Graph node functions for the multi-agent workflow.
"""
from typing_extensions import TypedDict
from typing import List, Dict, Any
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from tools.timing_tracker import timing_tracker
from utils.messaging import log_agent_activity
from utils.agent_factory import create_llm, create_weather_agent, create_email_agent


class SupervisorState(TypedDict):
    """State schema for the supervisor workflow."""
    messages: List
    next: str
    current_task: str
    completed_tasks: List[str]
    context: Dict[str, Any]


def weather_node(state: SupervisorState):
    """
    Weather specialist node for handling weather requests.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Command with updated state
    """
    timing_tracker.start_timer("weather_agent_processing")
    log_agent_activity("weather", "Processing weather request")
    
    # Create LLM and agent using standardized factory
    llm = create_llm()
    weather_agent = create_weather_agent(llm)
    
    # Process the request
    result = weather_agent.invoke(state)
    new_messages = result["messages"]
    
    timing_tracker.stop_timer("weather_agent_processing")
    log_agent_activity("weather", "Completed weather processing")
    
    # Update state and return to supervisor
    return Command(
        update={
            "messages": state["messages"] + [new_messages[-1]],
            "current_task": "weather_completed",
            "context": {**state.get("context", {}), "weather_processed": True},
            "completed_tasks": state.get("completed_tasks", []) + ["weather"]
        },
        goto="supervisor"
    )


def email_node(state: SupervisorState):
    """
    Email specialist node for handling email requests.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Command with updated state
    """
    timing_tracker.start_timer("email_agent_processing")
    log_agent_activity("email", "Processing email request")
    log_agent_activity("email", f"Current messages in conversation: {len(state['messages'])}")
    
    # Create LLM and agent using standardized factory
    llm = create_llm()
    email_agent = create_email_agent(llm)
    
    # Debug: Show recent messages for context
    recent_messages = state["messages"][-3:] if len(state["messages"]) >= 3 else state["messages"]
    for i, msg in enumerate(recent_messages):
        if hasattr(msg, 'content'):
            log_agent_activity("email", f"Message {i}: {msg.content[:100]}...")
    
    # Process the request
    result = email_agent.invoke(state)
    new_messages = result["messages"]
    
    log_agent_activity("email", f"Agent returned {len(new_messages)} messages")
    if new_messages:
        log_agent_activity("email", f"Last agent response: {new_messages[-1].content[:200]}...")
    
    # Check if send_email was actually called
    email_actually_sent = False
    for msg in new_messages:
        if hasattr(msg, 'content') and msg.content:
            if "✅ Email sent successfully" in msg.content:
                email_actually_sent = True
                break
    
    # Retry if email wasn't sent
    if not email_actually_sent:
        log_agent_activity("email", "Warning: send_email tool may not have been called!")
        # Force the agent to use the tool
        force_message = HumanMessage(
            content="Please actually use the send_email tool now to send the email. Do not just describe what you would do."
        )
        retry_state = {
            **state,
            "messages": state["messages"] + [force_message]
        }
        retry_result = email_agent.invoke(retry_state)
        new_messages = retry_result["messages"]
        log_agent_activity("email", f"Retry result: {new_messages[-1].content[:200]}...")
    
    timing_tracker.stop_timer("email_agent_processing")
    log_agent_activity("email", "Completed email processing")
    
    # Update state and return to supervisor
    return Command(
        update={
            "messages": state["messages"] + [new_messages[-1]],
            "current_task": "email_completed", 
            "context": {**state.get("context", {}), "email_processed": True},
            "completed_tasks": state.get("completed_tasks", []) + ["email"]
        },
        goto="supervisor"
    )


def supervisor_node(state: SupervisorState):
    """
    Supervisor node for routing and coordination.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Command with routing decision
    """
    timing_tracker.start_timer("supervisor_routing")
    log_agent_activity("supervisor", "Analyzing request and routing")
    
    # Import routing logic
    from graph.routing import determine_routing_decision
    
    # Get routing decision
    decision = determine_routing_decision(state)
    
    log_agent_activity("supervisor", f"Routing to: {decision['next_agent']}")
    log_agent_activity("supervisor", f"Reasoning: {decision['reasoning']}")
    
    timing_tracker.stop_timer("supervisor_routing")
    
    # Handle completion
    if decision["next_agent"] == "FINISH":
        from langgraph.graph import END
        decision["next_agent"] = END
    
    return Command(
        update={
            "next": decision["next_agent"],
            "current_task": f"routing_to_{decision['next_agent']}",
            **state
        },
        goto=decision["next_agent"]
    ) 