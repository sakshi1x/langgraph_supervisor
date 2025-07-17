"""
Supervisor agent for coordinating weather and email specialists.
"""
from langchain_openai import ChatOpenAI


def create_supervisor_agent(llm: ChatOpenAI = None) -> object:
    """
    Create the supervisor agent using standardized factory.
    
    Args:
        llm: Optional LLM instance (creates new one if not provided)
        
    Returns:
        Configured supervisor agent
    """
    from utils.agent_factory import create_agent
    from tools.handoff_tools import get_handoff_tools
    
    return create_agent(
        agent_name="supervisor",
        system_prompt_key="supervisor",
        tools=get_handoff_tools(),
        llm=llm
    )


def get_supervisor_agent_config() -> dict:
    """
    Get configuration specific to the supervisor agent.
    
    Returns:
        Configuration dictionary for supervisor agent
    """
    return {
        "name": "supervisor",
        "tools": ["handoff_to_weather", "handoff_to_email", "complete_task"],
        "capabilities": [
            "route_tasks_to_specialists",
            "coordinate_multi_step_workflows",
            "determine_task_completion",
            "manage_agent_handoffs"
        ],
        "managed_agents": ["weather_specialist", "email_specialist"]
    }


def validate_supervisor_agent_setup() -> bool:
    """
    Validate that the supervisor agent can be properly set up.
    
    Returns:
        True if setup is valid, False otherwise
    """
    try:
        # Check if handoff tools are available
        from tools.handoff_tools import get_handoff_tools
        tools = get_handoff_tools()
        return len(tools) >= 3  # Should have at least 3 handoff tools
    except ImportError:
        return False 