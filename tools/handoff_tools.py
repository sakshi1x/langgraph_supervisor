"""
Dynamic handoff tools for agent coordination using LangGraph.
"""

from typing import Annotated, Dict, List
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command, Send

def create_task_description_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )
    return handoff_tool

assign_to_weather_agent_with_description = create_task_description_handoff_tool(
    agent_name="weather_agent",
    description="Assign task to a weather agent.",
)

assign_to_email_agent_with_description = create_task_description_handoff_tool(
    agent_name="email_agent",
    description="Assign task to an email agent.",
)