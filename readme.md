# Multi-Agent Supervisor System

A LangGraph-based multi-agent system that uses a supervisor to coordinate between specialized agents for weather information and email sending tasks.

## Overview

This system implements a supervisor pattern where a main supervisor agent delegates tasks to specialized worker agents:
- **Weather Agent**: Fetches weather information for cities using the OpenWeatherMap API
- **Email Agent**: Sends emails with weather data or other content using SMTP

## Project Structure

```
supervisor/
├── readme.md                 # This file
├── requirements.txt          # Python dependencies
├── react_workflow.py        # Main workflow with ReAct agents
├── superviser_workflow.py   # Alternative supervisor workflow
├── weather_agent.py         # Weather agent implementation
└── email_agent.py           # Email agent implementation
```

## Features

- **Supervisor Coordination**: Intelligent task delegation between agents
- **Weather Data**: Real-time weather information for any city
- **Email Integration**: Automated email sending with weather data
- **ReAct Pattern**: Agents use reasoning and action cycles
- **LangGraph Workflows**: Robust state management and message passing

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Set up the following environment variables:

```bash
# API Keys
export OPENWEATHER_API_KEY="your_openweather_api_key"
export TAVILY_API_KEY="your_tavily_api_key"  # Optional

# Email Configuration
export SENDER_EMAIL="your_email@gmail.com"
export SENDER_PASSWORD="your_app_password"
export RECEIVER_EMAIL="recipient@example.com"
```

### 3. LLM Configuration

The system uses Ollama with local models. Update the model configuration in each file:

```python
llm = ChatOpenAI(
    api_key="ollama",
    model="llama3.1:latest",  # or "qwen2.5-coder:32b"
    base_url="http://localhost:11434",
    temperature=0.1,
    max_tokens=500
)
```

## Usage

### Option 1: React Workflow (`react_workflow.py`)

This implementation uses ReAct agents with explicit task delegation:

```python
# Run the workflow
python react_workflow.py
```

**Features:**
- Explicit task descriptions for delegation
- Sequential agent execution (weather first, then email)
- Detailed message formatting and debugging

### Option 2: Supervisor Workflow (`superviser_workflow.py`)

This implementation uses LangGraph's supervisor pattern:

```python
# Run the workflow
python superviser_workflow.py
```

**Features:**
- Built-in supervisor coordination
- Automatic task routing
- Full conversation history tracking

## Agent Capabilities

### Weather Agent
- **Tool**: `fetch_weather(city: str)`
- **Function**: Retrieves current weather data for any city
- **Data**: Temperature, humidity, wind speed, weather description
- **API**: OpenWeatherMap

### Email Agent
- **Tool**: `send_email(subject: str, body: str)`
- **Function**: Sends emails via SMTP
- **Features**: Can include weather data in email body
- **Provider**: Gmail SMTP

## Example Workflows

### Weather + Email Request
1. User asks for weather in London and to email the results
2. Supervisor delegates to weather agent
3. Weather agent fetches London weather data
4. Supervisor passes weather data to email agent
5. Email agent sends email with weather information

### Weather-Only Request
1. User asks for weather in Tokyo
2. Supervisor delegates to weather agent
3. Weather agent returns weather data
4. Workflow completes

### Email-Only Request
1. User asks to send an email with custom content
2. Supervisor delegates to email agent
3. Email agent sends the email
4. Workflow completes

## Configuration Files

### `react_workflow.py`
- Main workflow implementation
- ReAct agent pattern
- Explicit delegation tools
- Sequential execution logic

### `superviser_workflow.py`
- Alternative supervisor implementation
- LangGraph supervisor pattern
- Automatic task routing
- Full history tracking

### `weather_agent.py`
- Standalone weather agent
- OpenWeatherMap integration
- Structured weather data output

### `email_agent.py`
- Standalone email agent
- SMTP email sending
- Weather data integration

## Dependencies

- `langgraph`: Workflow orchestration
- `langgraph-supervisor`: Supervisor pattern implementation
- `langchain`: Core LLM integration
- `langchain-openai`: OpenAI-compatible models
- `requests`: HTTP requests for weather API
- `smtplib`: Email sending functionality

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are properly set
2. **Email Authentication**: Use app passwords for Gmail
3. **Ollama Connection**: Ensure Ollama is running on localhost:11434
4. **Model Loading**: Verify the specified model is available in Ollama

### Debug Mode

Both workflows include debug printing to help troubleshoot:
- Tool call logging
- Message flow tracking
- Agent state updates

## Extending the System

### Adding New Agents

1. Create a new agent file (e.g., `news_agent.py`)
2. Implement tools and agent logic
3. Add delegation tools to supervisor
4. Update supervisor prompts

### Custom Tools

1. Define new tools using the `@tool` decorator
2. Add tools to agent configurations
3. Update agent prompts for new capabilities

## License

This project is for educational and research purposes.
