"""
Configuration constants and settings for the multi-agent system.
"""
import os
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()


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
        
        # Supervisor Configuration
        "USE_DYNAMIC_SUPERVISOR_PROMPT": os.getenv("USE_DYNAMIC_SUPERVISOR_PROMPT", "true").lower() == "true",
        "SUPERVISOR_PROMPT_MODE": os.getenv("SUPERVISOR_PROMPT_MODE", "dynamic"),  # "dynamic" or "static"
    }


# Load configuration
CONFIG = load_config()


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