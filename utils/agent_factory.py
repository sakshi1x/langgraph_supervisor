"""
Agent factory with Langfuse automatic observation integration using @observe.
"""

import os
import asyncio
import atexit
from typing import List, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from config.constants import CONFIG, SYSTEM_PROMPTS

from langfuse import get_client, observe

# === Load environment variables from .env file ===
load_dotenv()
\
langfuse = get_client()

# === Gracefully flush Langfuse on exit ===
atexit.register(lambda: langfuse.flush())

# === Factory methods with @observe ===

@observe(name="create_llm")
def create_llm() -> ChatOpenAI:
    """Create an LLM instance with Langfuse tracing."""
    return ChatOpenAI(
        api_key="ollama",
        model=CONFIG["OLLAMA_MODEL"],
        base_url=CONFIG["OLLAMA_BASE_URL"],
        temperature=CONFIG["LLM_TEMPERATURE"],
    )

@observe(name="create_prompt_template")
def create_prompt_template(system_prompt_key: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPTS[system_prompt_key]),
        ("placeholder", "{messages}")
    ])

@observe(name="create_agent")
def create_agent(
    agent_name: str,
    system_prompt_key: str,
    tools: List[Any],
    llm: ChatOpenAI = None
) -> Any:
    llm = llm or create_llm()
    prompt = create_prompt_template(system_prompt_key)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
    )

    agent.name = agent_name
    agent.description = f"{agent_name.replace('_', ' ').title()} agent"
    return agent

@observe(name="create_weather_agent")
def create_weather_agent(llm: ChatOpenAI = None) -> Any:
    from tools.weather_tool import fetch_weather
    return create_agent(
        agent_name="weather_specialist",
        system_prompt_key="weather_specialist",
        tools=[fetch_weather],
        llm=llm
    )

@observe(name="create_email_agent")
def create_email_agent(llm: ChatOpenAI = None) -> Any:
    from tools.email_tool import send_email
    return create_agent(
        agent_name="email_specialist",
        system_prompt_key="email_specialist",
        tools=[send_email],
        llm=llm
    )

@observe(name="create_supervisor_agent")
def create_supervisor_agent(llm: ChatOpenAI = None) -> Any:
    from tools.handoff_tools import get_handoff_tools
    return create_agent(
        agent_name="supervisor",
        system_prompt_key="supervisor",
        tools=get_handoff_tools(),
        llm=llm
    )

AGENT_REGISTRY = {
    "weather_specialist": create_weather_agent,
    "email_specialist": create_email_agent,
    "supervisor": create_supervisor_agent
}

@observe(name="get_agent")
def get_agent(agent_type: str, llm: ChatOpenAI = None) -> Any:
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent type '{agent_type}'. Available: {list(AGENT_REGISTRY.keys())}"
        )
    return AGENT_REGISTRY[agent_type](llm)

@observe(name="list_available_agents")
def list_available_agents() -> List[str]:
    return list(AGENT_REGISTRY.keys())
