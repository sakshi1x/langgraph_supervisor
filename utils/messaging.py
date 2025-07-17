"""
Messaging utilities for pretty printing and conversation handling.
"""
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage


def pretty_print_message(message: BaseMessage, indent: bool = False) -> None:
    """
    Pretty print a single message.
    
    Args:
        message: The message to print
        indent: Whether to indent the output
    """
    try:
        pretty_message = message.pretty_repr(html=False)
    except AttributeError:
        # Fallback for messages without pretty_repr
        pretty_message = str(message)
        
    if not indent:
        print(pretty_message)
        return
        
    indented = "\n".join("\t" + line for line in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update: Dict[str, Any], last_message: bool = False) -> None:
    """
    Pretty print messages from a graph update.
    
    Args:
        update: The graph update containing messages
        last_message: Whether to only print the last message
    """
    is_subgraph = False
    
    # Handle subgraph updates
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return
        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    # Print messages from each node
    for node_name, node_update in update.items():
        if node_update is None or len(node_update) == 0:
            continue
            
        print(f"Node: {node_name}")
        
        if last_message:
            pretty_print_message(node_update[-1], indent=True)
        else:
            for message in node_update:
                pretty_print_message(message, indent=True)


def extract_latest_human_message(messages: List[BaseMessage]) -> str:
    """
    Extract the content of the latest human message.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Content of the latest human message, or empty string if none found
    """
    for message in reversed(messages):
        if hasattr(message, 'type') and message.type == 'human':
            return getattr(message, 'content', '')
        # Fallback for different message types
        elif hasattr(message, 'content') and 'human' in str(type(message)).lower():
            return message.content
            
    return ""


def extract_weather_data(messages: List[BaseMessage]) -> Optional[str]:
    """
    Extract weather data from conversation messages.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Weather data string if found, None otherwise
    """
    for message in messages:
        if hasattr(message, 'content') and message.content:
            content = str(message.content).lower()
            # Look for weather data patterns
            if ('weather in' in content and '°c' in content) or \
               ('temperature:' in content and '°c' in content):
                return message.content
                
    return None


def format_conversation_summary(messages: List[BaseMessage]) -> str:
    """
    Create a summary of the conversation for context.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Formatted conversation summary
    """
    if not messages:
        return "No conversation history"
        
    summary_parts = []
    message_count = len(messages)
    
    summary_parts.append(f"Conversation with {message_count} messages:")
    
    # Show last few messages
    recent_messages = messages[-3:] if len(messages) > 3 else messages
    
    for i, message in enumerate(recent_messages):
        if hasattr(message, 'content'):
            content = str(message.content)[:100]  # Truncate long messages
            message_type = getattr(message, 'type', 'unknown')
            summary_parts.append(f"  {message_type}: {content}...")
            
    return "\n".join(summary_parts)


def log_agent_activity(agent_name: str, activity: str, details: Optional[str] = None) -> None:
    """
    Log agent activity with consistent formatting.
    
    Args:
        agent_name: Name of the agent
        activity: What the agent is doing
        details: Optional additional details
    """
    emoji_map = {
        'weather': '🌤️',
        'email': '📧',
        'supervisor': '🧠',
        'system': '⚙️'
    }
    
    emoji = emoji_map.get(agent_name.lower(), '🤖')
    
    if details:
        print(f"{emoji} [{agent_name.upper()}] {activity}: {details}")
    else:
        print(f"{emoji} [{agent_name.upper()}] {activity}")


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error messages consistently.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"❌ [{context}] {error_type}: {error_msg}"
    else:
        return f"❌ {error_type}: {error_msg}" 