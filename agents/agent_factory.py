"""
Agent factory with Langfuse automatic observation integration using @observe.
"""

import os
import asyncio
import atexit
from typing import List, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langfuse import get_client, observe

from config.constants import CONFIG
from agents.prompts import get_updated_prompts, dynamic_prompt_manager

# Load environment variables from .env file
load_dotenv()

# Initialize Langfuse client
langfuse = get_client()

# Gracefully flush Langfuse on exit
atexit.register(lambda: langfuse.flush())


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
    """Create a prompt template for an agent using dynamic prompts."""
    # Get the latest prompts from the dynamic system
    system_prompts = get_updated_prompts()
    
    if system_prompt_key not in system_prompts:
        raise ValueError(f"Unknown system prompt key: {system_prompt_key}. Available: {list(system_prompts.keys())}")
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompts[system_prompt_key]),
        ("placeholder", "{messages}")
    ])


@observe(name="create_agent")
def create_agent(
    agent_name: str,
    system_prompt_key: str,
    tools: List[Any],
    llm: Optional[ChatOpenAI] = None
) -> Any:
    """Create a generic agent with the specified configuration."""
    if not agent_name or not system_prompt_key:
        raise ValueError("agent_name and system_prompt_key are required")
    
    llm = llm or create_llm()
    prompt = f"""{create_prompt_template(system_prompt_key)}"""
    
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
    )

    agent.name = agent_name
    agent.description = f"{agent_name.replace('_', ' ').title()} agent"
    return agent
