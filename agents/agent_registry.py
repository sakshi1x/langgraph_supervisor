"""
Agent registry for managing available agents.
"""

from typing import List, Any, Dict, Optional, Callable
from langchain_openai import ChatOpenAI
from langfuse import observe

from agents.agent_init import (
    create_weather_agent,
    create_email_agent, 
    create_supervisor_agent
)
from agents.prompts import refresh_prompts, add_agent_capability, remove_agent_capability

# Agent Registry
AGENT_REGISTRY = {
    "weather_specialist": create_weather_agent,
    "email_specialist": create_email_agent,
}

SUPERVISOR_REGISTRY = {
    "supervisor": create_supervisor_agent
}


@observe(name="get_agent")
def get_agent(agent_type: str, llm: Optional[ChatOpenAI] = None) -> Any:
    """Get an agent by type."""
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent type '{agent_type}'. Available: {list(AGENT_REGISTRY.keys())}"
        )
    return AGENT_REGISTRY[agent_type](llm)


@observe(name="list_available_agents")
def list_available_agents() -> List[str]:
    """List all available agent types."""
    return list(AGENT_REGISTRY.keys())


@observe(name="get_supervisor_agent")
def get_supervisor_agent(agent_type: str, llm: Optional[ChatOpenAI] = None) -> Any:
    """Get a supervisor agent by type."""
    if agent_type not in SUPERVISOR_REGISTRY:
        raise ValueError(
            f"Unknown supervisor agent type '{agent_type}'. Available: {list(SUPERVISOR_REGISTRY.keys())}"
        )
    return SUPERVISOR_REGISTRY[agent_type](llm)


@observe(name="list_available_supervisor_agents")
def list_available_supervisor_agents() -> List[str]:
    """List all available supervisor agent types."""
    return list(SUPERVISOR_REGISTRY.keys())


@observe(name="validate_agent")
def validate_agent(agent_name: str) -> List[str]:
    """Validate that an agent exists and can be created."""
    errors = []
    
    if agent_name not in AGENT_REGISTRY and agent_name not in SUPERVISOR_REGISTRY:
        errors.append(f"Unknown agent: {agent_name}")
        return errors
    
    try:
        # Try to create the agent to validate it works
        if agent_name in AGENT_REGISTRY:
            agent = get_agent(agent_name)
        else:
            agent = get_supervisor_agent(agent_name)
            
        if not agent:
            errors.append(f"Failed to create agent: {agent_name}")
    except Exception as e:
        errors.append(f"Error creating agent {agent_name}: {str(e)}")
    
    return errors


@observe(name="get_all_agents")
def get_all_agents() -> Dict[str, Any]:
    """Get all available agents (both regular and supervisor)."""
    all_agents = {}
    
    # Add regular agents
    for agent_name in AGENT_REGISTRY:
        try:
            all_agents[agent_name] = get_agent(agent_name)
        except Exception as e:
            print(f"Warning: Could not create agent {agent_name}: {e}")
    
    # Add supervisor agents
    for agent_name in SUPERVISOR_REGISTRY:
        try:
            all_agents[agent_name] = get_supervisor_agent(agent_name)
        except Exception as e:
            print(f"Warning: Could not create supervisor agent {agent_name}: {e}")
    
    return all_agents


# Dynamic Agent Management Functions

@observe(name="add_agent")
def add_agent(
    agent_name: str, 
    agent_creator: Callable, 
    description: str, 
    tools: List[str], 
    keywords: List[str],
    is_supervisor: bool = False
) -> bool:
    """
    Add a new agent to the registry.
    
    Args:
        agent_name: Name of the agent
        agent_creator: Function that creates the agent
        description: Description of what the agent does
        tools: List of tool names the agent uses
        keywords: List of keywords for agent discovery
        is_supervisor: Whether this is a supervisor agent
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add to appropriate registry
        if is_supervisor:
            SUPERVISOR_REGISTRY[agent_name] = agent_creator
        else:
            AGENT_REGISTRY[agent_name] = agent_creator
        
        # Add agent capabilities for dynamic prompts
        add_agent_capability(agent_name, description, tools, keywords)
        
        # Refresh prompts to include the new agent
        refresh_prompts()
        
        print(f"Successfully added agent: {agent_name}")
        return True
        
    except Exception as e:
        print(f"Error adding agent {agent_name}: {e}")
        return False


@observe(name="remove_agent")
def remove_agent(agent_name: str) -> bool:
    """
    Remove an agent from the registry.
    
    Args:
        agent_name: Name of the agent to remove
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Remove from registries
        if agent_name in AGENT_REGISTRY:
            del AGENT_REGISTRY[agent_name]
        elif agent_name in SUPERVISOR_REGISTRY:
            del SUPERVISOR_REGISTRY[agent_name]
        else:
            print(f"Agent {agent_name} not found in registry")
            return False
        
        # Remove agent capabilities
        remove_agent_capability(agent_name)
        
        # Refresh prompts to remove the agent
        refresh_prompts()
        
        print(f"Successfully removed agent: {agent_name}")
        return True
        
    except Exception as e:
        print(f"Error removing agent {agent_name}: {e}")
        return False


@observe(name="update_agent")
def update_agent(
    agent_name: str,
    agent_creator: Callable = None,
    description: str = None,
    tools: List[str] = None,
    keywords: List[str] = None,
    is_supervisor: bool = None
) -> bool:
    """
    Update an existing agent in the registry.
    
    Args:
        agent_name: Name of the agent to update
        agent_creator: New agent creator function (optional)
        description: New description (optional)
        tools: New tools list (optional)
        keywords: New keywords list (optional)
        is_supervisor: Whether this is a supervisor agent (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if agent exists
        if agent_name not in AGENT_REGISTRY and agent_name not in SUPERVISOR_REGISTRY:
            print(f"Agent {agent_name} not found in registry")
            return False
        
        # Update agent creator if provided
        if agent_creator is not None:
            if agent_name in AGENT_REGISTRY:
                AGENT_REGISTRY[agent_name] = agent_creator
            elif agent_name in SUPERVISOR_REGISTRY:
                SUPERVISOR_REGISTRY[agent_name] = agent_creator
        
        # Update capabilities if provided
        if description is not None or tools is not None or keywords is not None:
            from agents.prompts import AGENT_CAPABILITIES
            
            current_capabilities = AGENT_CAPABILITIES.get(agent_name, {})
            
            if description is not None:
                current_capabilities["description"] = description
            if tools is not None:
                current_capabilities["tools"] = tools
            if keywords is not None:
                current_capabilities["keywords"] = keywords
            
            add_agent_capability(agent_name, 
                               current_capabilities.get("description", ""),
                               current_capabilities.get("tools", []),
                               current_capabilities.get("keywords", []))
        
        # Refresh prompts
        refresh_prompts()
        
        print(f"Successfully updated agent: {agent_name}")
        return True
        
    except Exception as e:
        print(f"Error updating agent {agent_name}: {e}")
        return False


@observe(name="get_agent_info")
def get_agent_info(agent_name: str) -> Dict[str, Any]:
    """
    Get information about a specific agent.
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        Dict containing agent information
    """
    from agents.prompts import AGENT_CAPABILITIES
    
    info = {
        "name": agent_name,
        "exists": False,
        "is_supervisor": False,
        "capabilities": {}
    }
    
    if agent_name in AGENT_REGISTRY:
        info["exists"] = True
        info["is_supervisor"] = False
    elif agent_name in SUPERVISOR_REGISTRY:
        info["exists"] = True
        info["is_supervisor"] = True
    
    if info["exists"]:
        info["capabilities"] = AGENT_CAPABILITIES.get(agent_name, {})
    
    return info


@observe(name="list_all_agent_info")
def list_all_agent_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all agents in the registry.
    
    Returns:
        Dict mapping agent names to their information
    """
    all_info = {}
    
    # Add regular agents
    for agent_name in AGENT_REGISTRY:
        all_info[agent_name] = get_agent_info(agent_name)
    
    # Add supervisor agents
    for agent_name in SUPERVISOR_REGISTRY:
        all_info[agent_name] = get_agent_info(agent_name)
    
    return all_info