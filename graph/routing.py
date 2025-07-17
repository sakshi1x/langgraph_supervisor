"""
Routing logic for determining agent transitions and workflow decisions.
"""
from typing import Dict, Any, List
from typing_extensions import Literal
from utils.intent_analysis import (
    analyze_request_intent, 
    check_task_completion, 
    determine_next_action,
    get_intent_summary
)
from utils.messaging import log_agent_activity


RouterDecision = Dict[str, str]


def determine_routing_decision(state: Dict[str, Any]) -> RouterDecision:
    """
    Determine the next agent and routing decision based on current state.
    
    Args:
        state: Current supervisor state containing messages and context
        
    Returns:
        Dictionary with next_agent and reasoning
    """
    messages = state.get("messages", [])
    completed_tasks = state.get("completed_tasks", [])
    
    # Analyze user intent and completion status
    intent = analyze_request_intent(messages)
    completion = check_task_completion(messages)
    
    # Log analysis for debugging
    summary = get_intent_summary(intent, completion)
    log_agent_activity("supervisor", f"Intent analysis: {intent}")
    log_agent_activity("supervisor", f"Completion status: {completion}")
    log_agent_activity("supervisor", f"Completed tasks: {completed_tasks}")
    log_agent_activity("supervisor", f"Summary: {summary}")
    
    # Get routing decision using centralized logic
    decision = determine_next_action(intent, completion, completed_tasks)
    
    # If no clear decision, try supervisor agent fallback
    if decision["next_agent"] == "FINISH" and not any([
        completion.get("task_marked_complete"),
        completion.get("weather_completed") and not intent.get("needs_email"),
        completion.get("email_completed") and not intent.get("needs_weather"),
        completion.get("weather_completed") and completion.get("email_completed")
    ]):
        # Let supervisor agent make the decision
        decision = try_supervisor_agent_decision(state)
    
    return decision


def try_supervisor_agent_decision(state: Dict[str, Any]) -> RouterDecision:
    """
    Fallback to supervisor agent for making routing decisions.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Routing decision from supervisor agent
    """
    try:
        log_agent_activity("supervisor", "Using supervisor agent for routing decision")
        
        # Import here to avoid circular imports
        from utils.agent_factory import create_llm, create_supervisor_agent
        
        # Initialize supervisor agent using standardized factory
        llm = create_llm()
        supervisor_agent = create_supervisor_agent(llm)
        
        # Get supervisor's decision
        result = supervisor_agent.invoke(state)
        supervisor_response = result["messages"][-1]
        
        # Parse supervisor's response for routing decisions
        response_lower = supervisor_response.content.lower()
        
        if "transferring to weather agent" in response_lower:
            return {
                "next_agent": "weather_specialist",
                "reasoning": "Supervisor determined weather specialist is needed"
            }
        elif "transferring to email agent" in response_lower:
            return {
                "next_agent": "email_specialist", 
                "reasoning": "Supervisor determined email specialist is needed"
            }
        elif "task completed:" in response_lower:
            return {
                "next_agent": "FINISH",
                "reasoning": "Supervisor marked task as completed"
            }
        else:
            return {
                "next_agent": "FINISH",
                "reasoning": "Supervisor completed analysis - finishing workflow"
            }
            
    except Exception as e:
        log_agent_activity("supervisor", f"Agent decision failed, using fallback: {e}")
        return {
            "next_agent": "FINISH",
            "reasoning": "Fallback decision due to supervisor agent error"
        }


def validate_routing_decision(decision: RouterDecision) -> bool:
    """
    Validate that a routing decision is valid.
    
    Args:
        decision: The routing decision to validate
        
    Returns:
        True if decision is valid, False otherwise
    """
    valid_agents = ["weather_specialist", "email_specialist", "FINISH"]
    required_keys = ["next_agent", "reasoning"]
    
    # Check required keys
    if not all(key in decision for key in required_keys):
        return False
        
    # Check valid agent
    if decision["next_agent"] not in valid_agents:
        return False
        
    # Check reasoning is not empty
    if not decision["reasoning"].strip():
        return False
        
    return True


def get_routing_statistics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get statistics about the current routing state.
    
    Args:
        state: Current supervisor state
        
    Returns:
        Dictionary with routing statistics
    """
    messages = state.get("messages", [])
    completed_tasks = state.get("completed_tasks", [])
    
    intent = analyze_request_intent(messages)
    completion = check_task_completion(messages)
    
    return {
        "total_messages": len(messages),
        "completed_tasks_count": len(completed_tasks),
        "needs_weather": intent.get("needs_weather", False),
        "needs_email": intent.get("needs_email", False),
        "is_combined_request": intent.get("is_combined", False),
        "weather_completed": completion.get("weather_completed", False),
        "email_completed": completion.get("email_completed", False),
        "task_marked_complete": completion.get("task_marked_complete", False),
        "intent_confidence": intent.get("confidence", 0.0)
    }


def should_continue_workflow(state: Dict[str, Any]) -> bool:
    """
    Determine if the workflow should continue or finish.
    
    Args:
        state: Current supervisor state
        
    Returns:
        True if workflow should continue, False if it should finish
    """
    messages = state.get("messages", [])
    completed_tasks = state.get("completed_tasks", [])
    
    intent = analyze_request_intent(messages)
    completion = check_task_completion(messages)
    
    # Check if all requested tasks are complete
    weather_done = completion.get("weather_completed") or "weather" in completed_tasks
    email_done = completion.get("email_completed") or "email" in completed_tasks
    task_complete = completion.get("task_marked_complete")
    
    # Workflow should finish if:
    if task_complete:
        return False
    if intent.get("needs_weather") and weather_done and not intent.get("needs_email"):
        return False
    if intent.get("needs_email") and email_done and not intent.get("needs_weather"):
        return False
    if intent.get("is_combined") and weather_done and email_done:
        return False
        
    # Otherwise continue
    return True 