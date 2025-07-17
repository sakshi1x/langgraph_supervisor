"""
Handoff tools for agent coordination and task completion.
"""
from langchain_core.tools import tool


@tool
def handoff_to_weather(task_description: str = "Handle weather-related requests") -> str:
    """
    Transfer control to the weather specialist agent.
    
    Args:
        task_description: Description of the weather task to be handled
        
    Returns:
        Handoff confirmation message
    """
    return f"🌤️ Transferring to weather agent: {task_description}"


@tool
def handoff_to_email(task_description: str = "Handle email-related requests") -> str:
    """
    Transfer control to the email specialist agent.
    
    Args:
        task_description: Description of the email task to be handled
        
    Returns:
        Handoff confirmation message
    """
    return f"📧 Transferring to email agent: {task_description}"


@tool
def complete_task(summary: str) -> str:
    """
    Mark the current task as completed with a summary.
    
    Args:
        summary: Summary of what was accomplished
        
    Returns:
        Task completion confirmation
    """
    return f"✅ Task completed: {summary}"


def get_handoff_tools() -> list:
    """
    Get list of all handoff tools for supervisor agent.
    
    Returns:
        List of handoff tool functions
    """
    return [handoff_to_weather, handoff_to_email, complete_task] 