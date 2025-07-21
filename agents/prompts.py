import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Agent capabilities tracking
AGENT_CAPABILITIES = {}

# Sample dynamic JSON-like prompt config
PROMPT_CONFIG = {
    "weather_specialist": {
        "role": "You are a weather specialist.",
        "responsibilities": [
            "Fetch accurate weather information for requested cities using the fetch_weather tool",
            "Provide clear, well-formatted weather summaries",
            "Handle weather-related queries professionally"
        ],
        "rules": [
            "Always use the fetch_weather tool to get current weather data.",
            "Format your responses clearly and include all relevant weather information."
        ],
        "format": {
            "temperature": "Temperature in Celsius",
            "conditions": "Weather conditions (sunny, cloudy, rain, etc.)",
            "humidity": "Humidity percentage",
            "wind_speed": "Wind speed in m/s",
            "city": "City name"
        },
        "note": "After providing weather data, return control to the supervisor.",
        "templates": {
            "city_request": "Get weather for {city}",
            "weather_summary": "Weather in {city}: {conditions}, Temperature: {temperature}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s"
        }
    },
    "email_specialist": {
        "role": "You are an email specialist.",
        "critical_rules": [
            "ALWAYS call the send_email tool - never just describe what you would do",
            "Extract weather data from conversation history when needed",
            "Create professional email subjects and bodies"
        ],
        "email_format": {
            "subject": "Weather Report for {city}",
            "body": "Hello,\n\nHere is the current weather report for {city}:\n\n- Temperature: {temperature}°C\n- Conditions: {conditions}\n- Humidity: {humidity}%\n- Wind Speed: {wind_speed} m/s\n\nBest Regards,\nWeather Update Team"
        },
        "note": "Never just say you sent an email - actually call the send_email tool.",
        "templates": {
            "email_subject": "Weather Report for {city}",
            "email_body": "Hello,\n\nHere is the current weather report for {city}:\n\n- Temperature: {temperature}°C\n- Conditions: {conditions}\n- Humidity: {humidity}%\n- Wind Speed: {wind_speed} m/s\n\nBest Regards,\nWeather Update Team"
        }
    },
    "supervisor": {
        "role": "You are a multi-agent supervisor coordinating weather and email specialists.",
        "responsibilities": [
            "Analyze user requests to determine needed specialists",
            "Coordinate multi-step workflows (get weather then email it)",
            "Provide clear instructions to other agents"
        ],
        "coordination_rules": [
            "For weather requests: Ask weather specialist to get info",
            "For email requests: Ask email specialist to send emails",
            "For combined requests: Coordinate both agents in sequence",
            "Provide clear context and instructions"
        ],
        "workflow": [
            "Step 1: Ask weather specialist to get current weather for requested city",
            "Step 2: After weather data obtained, ask email specialist to send weather data via email",
            "Step 3: Confirm completion when done"
        ],
        "note": "Always provide clear instructions and monitor task completion.",
        "templates": {
            "weather_task": "Get the current weather for {city}.",
            "email_task": "Send an email with the current weather for {city}: {weather_summary}."
        }
    }
}

def load_prompts_from_file(file_path: str) -> Dict[str, Any]:
    """Load prompt configuration from external JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Prompt file {file_path} not found. Using default config.")
        return PROMPT_CONFIG
    except json.JSONDecodeError as e:
        print(f"Error parsing prompt file {file_path}: {e}. Using default config.")
        return PROMPT_CONFIG

def save_prompts_to_file(config: Dict[str, Any], file_path: str):
    """Save prompt configuration to external JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Prompts saved to {file_path}")
    except Exception as e:
        print(f"Error saving prompts to {file_path}: {e}")

def build_prompt(agent_name: str, config: dict) -> str:
    """Build prompt text dynamically from JSON-like config."""
    agent_config = config.get(agent_name, {})
    prompt_parts = []

    # Add role description
    if "role" in agent_config:
        prompt_parts.append(agent_config["role"])

    # Add lists like responsibilities, rules, coordination rules, etc.
    for key in ["responsibilities", "rules", "critical_rules", "coordination_rules", "workflow"]:
        if key in agent_config:
            prompt_parts.append(f"\n{key.replace('_', ' ').capitalize()}:")
            for idx, item in enumerate(agent_config[key], 1):
                prompt_parts.append(f"{idx}. {item}")

    # Add format sections if present
    if "format" in agent_config:
        prompt_parts.append("\nFORMAT:")
        for k, v in agent_config["format"].items():
            prompt_parts.append(f"- {v}")

    if "email_format" in agent_config:
        prompt_parts.append("\nEMAIL FORMAT:")
        for k, v in agent_config["email_format"].items():
            prompt_parts.append(f"- {k.capitalize()}: {v}")

    # Add notes if any
    if "note" in agent_config:
        prompt_parts.append(f"\nIMPORTANT:\n- {agent_config['note']}")

    return "\n".join(prompt_parts)

def build_prompt_with_vars(agent_name: str, config: dict, **variables) -> str:
    """Build prompt with template variable substitution."""
    prompt = build_prompt(agent_name, config)
    
    # Replace template variables
    try:
        return prompt.format(**variables)
    except KeyError as e:
        print(f"Warning: Missing template variable {e} for agent {agent_name}")
        return prompt

def get_template(agent_name: str, template_name: str, config: dict) -> str:
    """Get a specific template for an agent."""
    agent_config = config.get(agent_name, {})
    templates = agent_config.get("templates", {})
    return templates.get(template_name, "")

def build_contextual_prompt(agent_name: str, conversation_history: List[Dict], config: dict) -> str:
    """Build context-aware prompt based on conversation history."""
    base_prompt = build_prompt(agent_name, config)
    
    if not conversation_history:
        return base_prompt
    
    # Extract relevant context from conversation history
    context_parts = []
    recent_messages = conversation_history[-5:]  # Last 5 messages
    
    for msg in recent_messages:
        if msg.get("type") == "user":
            context_parts.append(f"User request: {msg.get('content', '')}")
        elif msg.get("type") == "assistant":
            context_parts.append(f"Previous response: {msg.get('content', '')}")
    
    if context_parts:
        context_section = "\n\nCONVERSATION CONTEXT:\n" + "\n".join(context_parts)
        return base_prompt + context_section
    
    return base_prompt

def build_adaptive_prompt(agent_name: str, user_request: str, config: dict) -> str:
    """Build adaptive prompt based on user request analysis."""
    base_prompt = build_prompt(agent_name, config)
    
    # Analyze user request to adapt prompt
    request_lower = user_request.lower()
    
    # Add specific instructions based on request type
    if "weather" in request_lower and "email" in request_lower:
        adaptive_instruction = "\n\nSPECIFIC INSTRUCTION: This is a combined weather and email request. First get the weather data, then send it via email."
    elif "weather" in request_lower:
        adaptive_instruction = "\n\nSPECIFIC INSTRUCTION: Focus on providing accurate weather information."
    elif "email" in request_lower:
        adaptive_instruction = "\n\nSPECIFIC INSTRUCTION: Focus on creating and sending professional emails."
    else:
        adaptive_instruction = "\n\nSPECIFIC INSTRUCTION: Analyze the request and provide appropriate assistance."
    
    return base_prompt + adaptive_instruction

# Enhanced Dynamic prompt manager for runtime prompt updates
class DynamicPromptManager:
    def __init__(self, config_file: Optional[str] = None):
        self.prompts = {}
        self.config = PROMPT_CONFIG
        self.config_file = config_file
        
        if config_file and os.path.exists(config_file):
            self.config = load_prompts_from_file(config_file)
        
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Load default prompts from config."""
        for agent_name, config in self.config.items():
            self.prompts[agent_name] = build_prompt(agent_name, self.config)
    
    def get_prompt(self, agent_name: str) -> str:
        """Get prompt for a specific agent."""
        return self.prompts.get(agent_name, "")
    
    def get_prompt_with_vars(self, agent_name: str, **variables) -> str:
        """Get prompt with variable substitution."""
        return build_prompt_with_vars(agent_name, self.config, **variables)
    
    def get_contextual_prompt(self, agent_name: str, conversation_history: List[Dict]) -> str:
        """Get context-aware prompt."""
        return build_contextual_prompt(agent_name, conversation_history, self.config)
    
    def get_adaptive_prompt(self, agent_name: str, user_request: str) -> str:
        """Get adaptive prompt based on user request."""
        return build_adaptive_prompt(agent_name, user_request, self.config)
    
    def update_prompt(self, agent_name: str, new_prompt: str):
        """Update prompt for a specific agent."""
        self.prompts[agent_name] = new_prompt
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update the entire prompt configuration."""
        self.config = new_config
        self._load_default_prompts()
    
    def reload_from_file(self):
        """Reload prompts from the config file."""
        if self.config_file and os.path.exists(self.config_file):
            self.config = load_prompts_from_file(self.config_file)
            self._load_default_prompts()
    
    def save_to_file(self, file_path: Optional[str] = None):
        """Save current config to file."""
        target_file = file_path or self.config_file
        if target_file:
            save_prompts_to_file(self.config, target_file)
    
    def get_all_prompts(self) -> dict:
        """Get all current prompts."""
        return self.prompts.copy()
    
    def reset_to_defaults(self):
        """Reset all prompts to default values."""
        self._load_default_prompts()
    
    def add_template(self, agent_name: str, template_name: str, template: str):
        """Add a new template for an agent."""
        if agent_name not in self.config:
            self.config[agent_name] = {}
        if "templates" not in self.config[agent_name]:
            self.config[agent_name]["templates"] = {}
        self.config[agent_name]["templates"][template_name] = template
        self._load_default_prompts()

# Global instance of the dynamic prompt manager
dynamic_prompt_manager = DynamicPromptManager()

def get_updated_prompts() -> dict:
    """Get the latest prompts from the dynamic prompt manager."""
    return dynamic_prompt_manager.get_all_prompts()

def refresh_prompts():
    """Refresh prompts to include any new agent capabilities."""
    global dynamic_prompt_manager
    dynamic_prompt_manager.reset_to_defaults()
    
    # Add prompts for agents in AGENT_CAPABILITIES that aren't in PROMPT_CONFIG
    for agent_name, capabilities in AGENT_CAPABILITIES.items():
        if agent_name not in PROMPT_CONFIG:
            # Create a basic prompt for the agent
            prompt_parts = [
                f"You are a {agent_name.replace('_', ' ')} specialist.",
                f"\nDescription: {capabilities.get('description', '')}",
                f"\nTools: {', '.join(capabilities.get('tools', []))}",
                f"\nKeywords: {', '.join(capabilities.get('keywords', []))}"
            ]
            dynamic_prompt_manager.prompts[agent_name] = "\n".join(prompt_parts)

def add_agent_capability(agent_name: str, description: str, tools: list, keywords: list):
    """Add or update agent capabilities."""
    AGENT_CAPABILITIES[agent_name] = {
        "description": description,
        "tools": tools,
        "keywords": keywords
    }

def remove_agent_capability(agent_name: str):
    """Remove agent capabilities."""
    if agent_name in AGENT_CAPABILITIES:
        del AGENT_CAPABILITIES[agent_name]

# Example usage and testing
if __name__ == "__main__":
    # Test basic prompt building
    print("=== Basic Prompts ===")
    print(build_prompt("weather_specialist", PROMPT_CONFIG))
    print("\n---\n")
    
    # Test template variables
    print("=== Template Variables ===")
    weather_prompt = build_prompt_with_vars("weather_specialist", PROMPT_CONFIG, city="London")
    print(weather_prompt)
    print("\n---\n")
    
    # Test contextual prompts
    print("=== Contextual Prompts ===")
    conversation_history = [
        {"type": "user", "content": "What's the weather like?"},
        {"type": "assistant", "content": "I can help you with weather information."}
    ]
    contextual_prompt = build_contextual_prompt("weather_specialist", conversation_history, PROMPT_CONFIG)
    print(contextual_prompt)
    print("\n---\n")
    
    # Test adaptive prompts
    print("=== Adaptive Prompts ===")
    adaptive_prompt = build_adaptive_prompt("supervisor", "Get weather for Paris and email it", PROMPT_CONFIG)
    print(adaptive_prompt)


