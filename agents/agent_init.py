"""
Agent initialization with Langfuse automatic observation integration.
"""

import os
import asyncio
import atexit
from typing import List, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langfuse import observe

from agents.agent_factory import create_agent, create_llm, create_prompt_template

# Load environment variables from .env file
load_dotenv()


def _create_mock_weather_tool():
    """Create a mock weather tool for testing."""
    def mock_fetch_weather(city: str) -> str:
        return f"Weather data for {city}: Temperature 22°C, Conditions: Sunny"
    return mock_fetch_weather


def _create_mock_email_tool():
    """Create a mock email tool for testing."""
    def mock_send_email(subject: str, body: str, to_email: str = None) -> str:
        return f"Email sent: {subject} to {to_email or 'default@example.com'}"
    return mock_send_email


def _create_mock_handoff_tools():
    """Create mock handoff tools for testing."""
    def mock_handoff_to_weather(task: str) -> str:
        return f"Handed off weather task: {task}"
    
    def mock_handoff_to_email(task: str) -> str:
        return f"Handed off email task: {task}"
    
    def mock_complete_task(result: str) -> str:
        return f"Task completed: {result}"
    
    return [mock_handoff_to_weather, mock_handoff_to_email, mock_complete_task]


@observe(name="create_weather_agent")
def create_weather_agent(llm: Optional[ChatOpenAI] = None) -> Any:
    """Create a weather specialist agent."""
    try:
        from tools.weather_tool import fetch_weather
        tools = [fetch_weather]
    except ImportError:
        tools = [_create_mock_weather_tool()]
    
    return create_agent(
        agent_name="weather_specialist",
        system_prompt_key="weather_specialist",
        tools=tools,
        llm=llm
    )


@observe(name="create_email_agent")
def create_email_agent(llm: Optional[ChatOpenAI] = None) -> Any:
    """Create an email specialist agent."""
    try:
        from tools.email_tool import send_email
        tools = [send_email]
    except ImportError:
        tools = [_create_mock_email_tool()]
    
    return create_agent(
        agent_name="email_specialist",
        system_prompt_key="email_specialist",
        tools=tools,
        llm=llm
    )


@observe(name="create_supervisor_agent")
def create_supervisor_agent(llm: Optional[ChatOpenAI] = None) -> Any:
    """Create a supervisor agent."""
    try:
        from tools.handoff_tools import (
            assign_to_weather_agent_with_description,
            assign_to_email_agent_with_description,
       
        )
        tools = [
            assign_to_weather_agent_with_description,
            assign_to_email_agent_with_description,
    
        ]
    except ImportError:
        tools = []
    
    # Create a custom supervisor function that handles the tools properly
    def supervisor_node(state):
        """Supervisor node that handles handoff tools."""
        current_llm = llm or create_llm()
        prompt = create_prompt_template("supervisor")
        
        # Create the agent with tools
        agent = create_react_agent(
            model=current_llm,
            tools=tools,
            prompt=prompt
        )
        
        # Execute the agent
        return agent.invoke(state)
    
    return supervisor_node
