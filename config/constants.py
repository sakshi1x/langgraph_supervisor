"""
Configuration constants and settings for the multi-agent system.
"""
import os
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()

# Load environment variables
def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables with fallbacks."""
    return {
        # LLM Configuration
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", ""),
        "LLM_TEMPERATURE": float(os.getenv("LLM_TEMPERATURE", "0.4")),
        
        # Email Configuration
        "SENDER_EMAIL": os.getenv("SENDER_EMAIL", ""),
        "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD", ""),
        "RECEIVER_EMAIL": os.getenv("RECEIVER_EMAIL", ""),
        "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "465")),
        
        
        
        
        # Weather API Configuration
        "OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY", ""),
        
        # System Configuration
        "RECURSION_LIMIT": int(os.getenv("RECURSION_LIMIT", "10")),
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
        "TIMEOUT_SECONDS": int(os.getenv("TIMEOUT_SECONDS", "30")),
    }

# Load configuration
CONFIG = load_config()

# Validate required environment variables
def validate_config() -> None:
    """Validate that all required configuration is present."""
    required_vars = [
        "SENDER_EMAIL",
        "SENDER_PASSWORD", 
        "RECEIVER_EMAIL",
        "OPENWEATHER_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not CONFIG.get(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please set them in your .env file or environment."
        )

# System Messages and Prompts
SYSTEM_PROMPTS = {
    "weather_specialist": """You are a weather specialist. Your role is to:
    1. Fetch accurate weather information for requested cities using the fetch_weather tool
    2. Provide clear, well-formatted weather summaries
    3. Handle weather-related queries professionally
    
    Always use the fetch_weather tool to get current weather data.
    Format your responses clearly and include all relevant weather information.""",
    
    "email_specialist": """You are an email specialist. You MUST use the send_email tool for any email request.

    CRITICAL RULES:
    1. ALWAYS call the send_email tool - never just describe what you would do
    2. Extract weather data from conversation history when needed
    3. Create professional email subjects and bodies
    
    For weather emails:
    - Look through conversation messages for weather data (temperature, conditions, etc.)
    - Include all weather details in the email body
    - Use the exact subject requested by the user
    
    NEVER just say you sent an email - you MUST actually call the send_email tool with proper subject and body parameters.
    
    If you see weather information in the conversation, extract it and format it nicely in the email body.""",
    
    "supervisor": """You are a multi-agent supervisor coordinating weather and email specialists.

    RESPONSIBILITIES:
    - Analyze user requests to determine which specialist(s) are needed
    - Route tasks to appropriate agents using handoff tools
    - Coordinate multi-step workflows (e.g., get weather then email it)
    - Determine when all tasks are completed

    ROUTING RULES:
    - For weather requests: use handoff_to_weather tool
    - For email requests: use handoff_to_email tool  
    - For combined requests: coordinate both agents in sequence
    - When all tasks done: use complete_task tool

    HANDOFF TOOL USAGE:
    - Include clear task descriptions when using handoff tools
    - Monitor conversation for task completion
    - Only use complete_task when user's request is fully satisfied
    
    Always think step-by-step about what the user needs and route accordingly."""
}

# API Endpoints
API_ENDPOINTS = {
    "openweather": "http://api.openweathermap.org/data/2.5/weather"
}

# Timing and Performance
TIMING_CONFIG = {
    "enable_timing": True,
    "enable_detailed_logging": True,
    "timing_precision": 3  # decimal places
} 