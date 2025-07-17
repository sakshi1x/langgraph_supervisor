"""
Email specialist agent for handling email-related requests.
"""
from langchain_openai import ChatOpenAI


def create_email_agent(llm: ChatOpenAI = None) -> object:
    """
    Create the email specialist agent using standardized factory.
    
    Args:
        llm: Optional LLM instance (creates new one if not provided)
        
    Returns:
        Configured email agent
    """
    from utils.agent_factory import create_agent
    from tools.email_tool import send_email
    
    return create_agent(
        agent_name="email_specialist",
        system_prompt_key="email_specialist",
        tools=[send_email],
        llm=llm
    )


def get_email_agent_config() -> dict:
    """
    Get configuration specific to the email agent.
    
    Returns:
        Configuration dictionary for email agent
    """
    return {
        "name": "email_specialist",
        "tools": ["send_email"],
        "capabilities": [
            "send_email_messages",
            "format_email_content",
            "handle_email_requests",
            "extract_weather_data_for_emails"
        ],
        "required_env_vars": ["SENDER_EMAIL", "SENDER_PASSWORD", "RECEIVER_EMAIL"]
    }


def validate_email_agent_setup() -> bool:
    """
    Validate that the email agent can be properly set up.
    
    Returns:
        True if setup is valid, False otherwise
    """
    from tools.email_tool import validate_email_config
    return validate_email_config() 