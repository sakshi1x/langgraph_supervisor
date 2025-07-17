"""
Weather specialist agent for handling weather-related requests.
"""
from langchain_openai import ChatOpenAI


def create_weather_agent(llm: ChatOpenAI = None) -> object:
    """
    Create the weather specialist agent using standardized factory.
    
    Args:
        llm: Optional LLM instance (creates new one if not provided)
        
    Returns:
        Configured weather agent
    """
    from utils.agent_factory import create_agent
    from tools.weather_tool import fetch_weather
    
    return create_agent(
        agent_name="weather_specialist",
        system_prompt_key="weather_specialist",
        tools=[fetch_weather],
        llm=llm
    )


def get_weather_agent_config() -> dict:
    """
    Get configuration specific to the weather agent.
    
    Returns:
        Configuration dictionary for weather agent
    """
    return {
        "name": "weather_specialist",
        "tools": ["fetch_weather"],
        "capabilities": [
            "fetch_current_weather",
            "format_weather_reports",
            "handle_weather_queries"
        ],
        "required_env_vars": ["OPENWEATHER_API_KEY"]
    }


def validate_weather_agent_setup() -> bool:
    """
    Validate that the weather agent can be properly set up.
    
    Returns:
        True if setup is valid, False otherwise
    """
    from tools.weather_tool import validate_weather_api
    return validate_weather_api() 