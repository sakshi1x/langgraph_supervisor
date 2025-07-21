

import getpass
import os
import requests
from typing import Annotated
from email.mime.text import MIMEText
import smtplib
from agents.agent_factory import create_llm
from agents.agent_registry import get_agent, get_supervisor_agent
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command, Send
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langchain_core.messages import convert_to_messages
from IPython.display import display, Image

from agents.agent_factory import create_llm





# Set API keys
llm = create_llm()

# Pretty print helper functions
def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return
    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return
        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        # Skip if node_update is None or doesn't have messages
        if node_update is None or "messages" not in node_update or node_update["messages"] is None:
            print(f"Node {node_name}: No messages to display")
            continue
            
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label
        print(update_label)
        print("\n")
        
        try:
            messages = convert_to_messages(node_update["messages"])
            if last_message:
                messages = messages[-1:]
            for m in messages:
                pretty_print_message(m, indent=is_subgraph)
            print("\n")
        except Exception as e:
            print(f"Error processing messages for {node_name}: {e}")
            print("\n")

# 4. Create delegation tasks with explicit task descriptions
email_agent = get_agent("email_specialist")
weather_agent = get_agent("weather_specialist")

supervisor_agent_with_description = get_supervisor_agent("supervisor")
# Create the supervisor graph with proper structure
supervisor_with_description = (
    StateGraph(MessagesState)
    .add_node("supervisor", supervisor_agent_with_description)
    .add_node("weather_agent", weather_agent)
    .add_node("email_agent", email_agent)
    .add_edge(START, "supervisor")
    .add_edge("weather_agent", "supervisor")
    .add_edge("email_agent", "supervisor")
    .add_edge("weather_agent", END)
    
    .compile()
)

# Run supervisor with task description
print("\n=== Running supervisor with task descriptions ===")
try:
    for chunk in supervisor_with_description.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "send an email of kathmandu weather .",
                }
            ]
        },
        subgraphs=True,
    ):
        pretty_print_messages(chunk, last_message=True)
except Exception as e:
    print(f"Error running supervisor with descriptions: {e}")