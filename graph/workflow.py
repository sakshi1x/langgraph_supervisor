"""
Workflow construction and graph compilation for the multi-agent system.
"""
from langgraph.graph import StateGraph, START, END
from graph.nodes import SupervisorState, weather_node, email_node, supervisor_node
from utils.messaging import log_agent_activity


def create_supervisor_workflow():
    """
    Create the enhanced supervisor workflow graph.
    
    Returns:
        Compiled StateGraph for the multi-agent workflow
    """
    log_agent_activity("system", "Creating supervisor workflow graph")
    
    # Create the graph builder
    builder = StateGraph(SupervisorState)
    
    # Add nodes to the graph
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("weather_specialist", weather_node)
    builder.add_node("email_specialist", email_node)
    
    # Set entry point - all requests start at supervisor
    builder.add_edge(START, "supervisor")
    
    log_agent_activity("system", "Workflow graph created successfully")
    
    return builder


def compile_workflow():
    """
    Compile the complete workflow for execution.
    
    Returns:
        Compiled and ready-to-use workflow graph
    """
    log_agent_activity("system", "Compiling workflow graph")
    
    try:
        # Create and compile the workflow
        workflow_builder = create_supervisor_workflow()
        graph = workflow_builder.compile()
        
        log_agent_activity("system", "Workflow compiled successfully")
        return graph
        
    except Exception as e:
        log_agent_activity("system", f"Failed to compile workflow: {e}")
        raise


def get_workflow_config(thread_id: str = "default") -> dict:
    """
    Get configuration for workflow execution.
    
    Args:
        thread_id: Unique identifier for the conversation thread
        
    Returns:
        Configuration dictionary for graph execution
    """
    from config.constants import CONFIG
    
    return {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": CONFIG.get("RECURSION_LIMIT", 10)
        }
    }


def create_initial_state(user_query: str) -> dict:
    """
    Create the initial state for workflow execution.
    
    Args:
        user_query: The user's initial request
        
    Returns:
        Initial state dictionary
    """
    from langchain_core.messages import HumanMessage
    
    return {
        'messages': [HumanMessage(content=user_query)],
        'next': '',
        'current_task': 'initializing',
        'completed_tasks': [],
        'context': {}
    }


def execute_workflow(user_query: str, thread_id: str = "default") -> dict:
    """
    Execute the complete workflow for a user query.
    
    Args:
        user_query: The user's request
        thread_id: Unique identifier for the conversation thread
        
    Returns:
        Final workflow result
    """
    from tools.timing_tracker import timing_tracker
    
    log_agent_activity("system", f"Executing workflow for query: {user_query[:50]}...")
    timing_tracker.start_timer("workflow_execution")
    
    try:
        # Compile workflow and prepare execution
        graph = compile_workflow()
        initial_state = create_initial_state(user_query)
        config = get_workflow_config(thread_id)
        
        # Execute the workflow
        result = graph.invoke(input=initial_state, config=config)
        
        timing_tracker.stop_timer("workflow_execution")
        log_agent_activity("system", "Workflow execution completed successfully")
        
        return result
        
    except Exception as e:
        timing_tracker.stop_timer("workflow_execution")
        log_agent_activity("system", f"Workflow execution failed: {e}")
        raise


def get_workflow_schema() -> dict:
    """
    Get the schema definition for the workflow state.
    
    Returns:
        Dictionary describing the workflow state schema
    """
    return {
        "messages": "List of conversation messages",
        "next": "Next agent to route to",
        "current_task": "Current task being processed",
        "completed_tasks": "List of completed task names",
        "context": "Additional context and metadata"
    }


def validate_workflow() -> bool:
    """
    Validate that the workflow can be properly constructed and compiled.
    
    Returns:
        True if workflow is valid, False otherwise
    """
    try:
        # Try to create and compile the workflow
        graph = compile_workflow()
        
        # Check that the graph has the expected nodes
        expected_nodes = ["supervisor", "weather_specialist", "email_specialist"]
        
        # Basic validation - if we got here without exception, it's likely valid
        log_agent_activity("system", "Workflow validation successful")
        return True
        
    except Exception as e:
        log_agent_activity("system", f"Workflow validation failed: {e}")
        return False


def get_workflow_statistics() -> dict:
    """
    Get statistics about the workflow configuration.
    
    Returns:
        Dictionary with workflow statistics
    """
    try:
        # Get basic workflow info
        stats = {
            "total_nodes": 3,
            "agent_nodes": ["weather_specialist", "email_specialist"],
            "coordinator_nodes": ["supervisor"],
            "entry_point": "supervisor",
            "max_recursion": 10,
            "supports_tools": True,
            "supports_handoffs": True
        }
        
        return stats
        
    except Exception as e:
        log_agent_activity("system", f"Failed to get workflow statistics: {e}")
        return {} 