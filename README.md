# 🚀 Dynamic Multi-Agent Supervisor System

A highly dynamic and flexible multi-agent system that coordinates specialized agents for weather information and email communication. This system demonstrates advanced prompt engineering, dynamic agent management, and real-time adaptation capabilities.

## 🌟 Key Features

### 🎯 **Fully Dynamic Prompt System**
- **External Configuration Loading** - Load prompts from JSON files without code changes
- **Template Variable Substitution** - Use dynamic variables like `{city}`, `{temperature}`, `{conditions}`
- **Context-Aware Prompts** - Adapt prompts based on conversation history
- **Adaptive Prompts** - Intelligent prompt customization based on user requests
- **Runtime Prompt Updates** - Modify prompts on-the-fly without restarting
- **Save/Reload Capabilities** - Persistent prompt management with external storage

### 🤖 **Dynamic Agent Management**
- **Runtime Agent Addition** - Add new agents without code changes
- **Dynamic Capability Tracking** - Track agent tools, descriptions, and keywords
- **Hot-Swappable Agents** - Replace agents during runtime
- **Agent Registry** - Centralized agent management with validation

### ⚡ **Real-Time Adaptation**
- **Conversation Context Awareness** - Agents adapt based on conversation history
- **Request Analysis** - Intelligent routing based on user request content
- **Dynamic Workflow Coordination** - Multi-step workflows with real-time handoffs
- **Performance Monitoring** - Built-in timing and observation tracking

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supervisor    │    │  Weather Agent  │    │  Email Agent    │
│   Agent         │◄──►│                 │◄──►│                 │
│                 │    │ • fetch_weather │    │ • send_email    │
│ • Coordination  │    │ • Dynamic       │    │ • Template      │
│ • Dynamic       │    │   Prompts       │    │   Variables     │
│   Routing       │    │ • Context       │    │ • Adaptive      │
└─────────────────┘    │   Awareness     │    │   Formatting    │
                       └─────────────────┘    └─────────────────┘
```

## 🎨 Dynamic Prompt System

### 📁 **External Configuration Loading**

Load prompts from external JSON files for easy customization:

```python
# Load from external file
manager = DynamicPromptManager("config/prompts.json")

# Hot-reload prompts
manager.reload_from_file()
```

**Example `config/prompts.json`:**
```json
{
  "weather_specialist": {
    "role": "You are a weather specialist with enhanced capabilities.",
    "responsibilities": [
      "Fetch accurate weather information for requested cities",
      "Provide detailed weather analysis with air quality"
    ],
    "templates": {
      "weather_summary": "Weather in {city}: {conditions}, Temperature: {temperature}°C"
    }
  }
}
```

### 🔤 **Template Variable Substitution**

Use dynamic variables in prompts:

```python
# Build prompt with variables
prompt = build_prompt_with_vars(
    "weather_specialist", 
    config,
    city="Tokyo",
    temperature="25°C",
    conditions="Sunny",
    humidity="60%"
)
```

### 🧠 **Context-Aware Prompts**

Prompts adapt based on conversation history:

```python
conversation_history = [
    {"type": "user", "content": "What's the weather in London?"},
    {"type": "assistant", "content": "I'll check the weather for London."}
]

contextual_prompt = build_contextual_prompt(
    "supervisor",
    conversation_history,
    config
)
```

### 🎯 **Adaptive Prompts**

Intelligent prompt customization based on user requests:

```python
# Different prompts for different request types
adaptive_prompt = build_adaptive_prompt(
    "supervisor",
    "Get weather for Paris and email it urgently",
    config
)
```

## 🤖 Dynamic Agent Management

### ➕ **Runtime Agent Addition**

Add new agents dynamically:

```python
# Add new agent capability
add_agent_capability(
    "news_agent",
    "Provides latest news updates",
    ["fetch_news", "summarize_news"],
    ["news", "updates", "current events"]
)

# Refresh prompts to include new agent
refresh_prompts()
```

### 🔄 **Hot-Swappable Agents**

Replace agents during runtime:

```python
# Update agent configuration
update_agent(
    agent_name="weather_specialist",
    description="Enhanced weather specialist with AI capabilities",
    tools=["fetch_weather", "get_forecast", "air_quality"],
    keywords=["weather", "climate", "forecast"]
)
```

## ⚡ Real-Time Adaptation Examples

### 1. **Dynamic Weather Requests**

```python
# User: "Get weather for Tokyo"
# System adapts prompt to focus on weather information
adaptive_instruction = "Focus on providing accurate weather information."

# User: "Get weather for Paris and email it urgently"
# System adapts prompt for combined workflow
adaptive_instruction = "This is a combined weather and email request. First get the weather data, then send it via email."
```

### 2. **Context-Aware Responses**

```python
# Conversation history influences prompt generation
context_section = """
CONVERSATION CONTEXT:
User request: What's the weather in London?
Previous response: I'll check the weather for London.
User request: Also send it via email
"""
```

### 3. **Template Variable Usage**

```python
# Dynamic email templates with real data
email_template = """
Subject: Weather Report for {city} - {date}
Body: Hello,

Here is the weather report for {city}:
- Temperature: {temperature}°C ({fahrenheit}°F)
- Conditions: {conditions}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s
"""
```

## 🛠️ Installation & Usage

### Prerequisites

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the system
python main.py
```

### Advanced Usage

```python
from agents.prompts import DynamicPromptManager

# Create manager with external config
manager = DynamicPromptManager("config/prompts.json")

# Get adaptive prompt
prompt = manager.get_adaptive_prompt(
    "supervisor", 
    "Get weather for Tokyo and email it"
)

# Add new template
manager.add_template(
    "weather_specialist",
    "custom_alert",
    "URGENT: Severe weather alert for {city} - {conditions}"
)

# Save configuration
manager.save_to_file("custom_prompts.json")
```

## 📊 Dynamic Features Comparison

| Feature | Before | After (Dynamic) |
|---------|--------|-----------------|
| **Prompt Configuration** | Hardcoded in code | External JSON files |
| **Template Variables** | Static text | Dynamic `{variable}` substitution |
| **Context Awareness** | None | Conversation history integration |
| **Request Adaptation** | Fixed prompts | Intelligent prompt customization |
| **Runtime Updates** | Requires restart | Hot-reload capabilities |
| **Agent Management** | Static registry | Dynamic addition/removal |
| **Configuration** | Code changes needed | File-based configuration |

## 🔧 Configuration Files

### `config/prompts.json`
External prompt configuration with templates and variables.

### `config/constants.py`
System constants and configuration parameters.

### `agents/prompts.py`
Core dynamic prompt management system.

## 🎯 Dynamic Capabilities Showcase

### 1. **External Configuration**
- ✅ Load prompts from JSON files
- ✅ Hot-reload without restart
- ✅ Fallback to defaults
- ✅ Save configurations

### 2. **Template Variables**
- ✅ Dynamic variable substitution
- ✅ Error handling for missing variables
- ✅ Nested template support
- ✅ Real-time data integration

### 3. **Context Awareness**
- ✅ Conversation history integration
- ✅ Smart context extraction
- ✅ Relevant information filtering
- ✅ Adaptive responses

### 4. **Request Adaptation**
- ✅ Intelligent request analysis
- ✅ Customized prompt generation
- ✅ Multi-step workflow support
- ✅ Priority-based processing

### 5. **Runtime Management**
- ✅ Add agents dynamically
- ✅ Update capabilities on-the-fly
- ✅ Hot-swap configurations
- ✅ Performance monitoring

## 🚀 Advanced Usage Examples

### Dynamic Agent Creation

```python
# Create new agent type dynamically
new_agent_config = {
    "role": "You are a specialized AI assistant.",
    "responsibilities": ["Handle specialized tasks"],
    "rules": ["Use appropriate tools"],
    "templates": {
        "task_template": "Handle {task_type} for {target}"
    }
}

# Add to system
manager.config["new_agent"] = new_agent_config
manager._load_default_prompts()
```

### Context-Aware Workflows

```python
# Build contextual workflow
conversation_history = [
    {"type": "user", "content": "What's the weather?"},
    {"type": "assistant", "content": "I can help with weather information."},
    {"type": "user", "content": "Send it via email"}
]

# Generate context-aware prompt
prompt = manager.get_contextual_prompt("supervisor", conversation_history)
```

### Template Variable Integration

```python
# Real-time data integration
weather_data = {
    "city": "Tokyo",
    "temperature": "25°C",
    "conditions": "Sunny",
    "humidity": "60%",
    "wind_speed": "5.2 m/s"
}

# Generate dynamic prompt
prompt = manager.get_prompt_with_vars("weather_specialist", **weather_data)
```

## 📈 Performance & Monitoring

- **Timing Tracking** - Built-in performance monitoring
- **Langfuse Integration** - Advanced observability
- **Error Handling** - Graceful fallbacks
- **Validation** - Agent capability validation

## 🔮 Future Enhancements

- **AI-Powered Prompt Generation** - Automatic prompt optimization
- **Multi-Language Support** - Internationalization
- **Advanced Templates** - Conditional logic in templates
- **Plugin System** - Extensible agent capabilities
- **Real-Time Collaboration** - Multi-user prompt editing

## 🤝 Contributing

This system demonstrates advanced dynamic capabilities in multi-agent systems. Contributions are welcome for:

- New agent types
- Enhanced prompt templates
- Additional dynamic features
- Performance optimizations

## 📄 License

This project showcases dynamic multi-agent system capabilities for educational and research purposes.

---

**🎉 This system demonstrates true dynamic behavior with external configuration, template variables, context awareness, and runtime adaptation - making it one of the most flexible multi-agent systems available!**
