

import getpass
import os
import requests
from typing import Annotated
from email.mime.text import MIMEText
import smtplib
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command, Send
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langchain_core.messages import convert_to_messages
from IPython.display import display, Image

# Set API keys
os.environ["TAVILY_API_KEY"] = ""
os.environ["OPENWEATHER_API_KEY"] = ""

SENDER_EMAIL = 
SENDER_PASSWORD = 
RECEIVER_EMAIL =

# === LLM Model Setup ===
llm = ChatOpenAI(
    api_key="ollama",
    model="llama3.1:latest",
    base_url=,
    temperature=0.1,
    max_tokens=500
)

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

# 1. Create worker agents
# Weather agent
@tool
def fetch_weather(city: str) -> str:
    """Fetch weather information for a given city."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    city = city.strip().strip('"').strip("'")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_info = (
            f"Weather in {city}: {data['weather'][0]['description'].title()}, "
            f"Temperature: {data['main']['temp']}°C, "
            f"Humidity: {data['main']['humidity']}%, "
            f"Wind Speed: {data['wind']['speed']} m/s"
        )
        print(f"🌤️ [DEBUG] Weather fetched: {weather_info}")
        return weather_info
    except requests.RequestException as e:
        return f"Error fetching weather for {city}: {str(e)}"
    except KeyError as e:
        return f"Error parsing weather data for {city}: {str(e)}"

weather_agent = create_react_agent(
    model=llm,
    tools=[fetch_weather],
    prompt=(
        "You are a weather agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with weather-related tasks, such as fetching weather data for a city\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text"
    ),
    name="weather_agent",
)

# Email agent
@tool
def send_email(subject: str, body: str) -> str:
    """Send an email with the given subject and body."""
    try:
        print(f"📤 [DEBUG] Actually invoking send_email() with subject: {subject}")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        success_msg = f"✅ Email sent successfully to {RECEIVER_EMAIL} with subject '{subject}'"
        print(success_msg)
        return success_msg
    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Check your email credentials."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {str(e)}"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

email_agent = create_react_agent(
    model=llm,
    tools=[send_email],
    prompt=(
        "You are an email agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with email-related tasks, such as sending emails\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text"
    ),
    name="email_agent",
)


# 4. Create delegation tasks with explicit task descriptions
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

supervisor_agent_with_description = create_react_agent(
    model=llm,
    tools=[
        assign_to_weather_agent_with_description,
        assign_to_email_agent_with_description,
    ],
prompt=(
    "You are a supervisor managing two agents:\n"
    "- If there are any weather-related tasks, assign **ALL** of them individually and completely to the weather agent **FIRST**.\n"
    "- After completing all weather tasks, if there are any email-related tasks, assign **ALL** of them individually and completely to the email agent **NEXT**.\n"
    "- If there are only weather or only email tasks, assign those tasks only to the respective agent.\n"
    "- You **MUST** always call the agent responsible for the tasks present.\n"
    "- Handle only one agent at a time; do **NOT** call agents in parallel.\n"
    "- Never do any work yourself; only delegate tasks in the proper order.\n"
    "- Always follow the order: weather agent first, then email agent, if both are present."
),
name="supervisor",
)


supervisor_with_description = (
    StateGraph(MessagesState)
    .add_node(
        supervisor_agent_with_description, destinations=("weather_agent", "email_agent")
    )
    .add_node(weather_agent)
    .add_node(email_agent)
    .add_edge(START, "supervisor")
    .add_edge("weather_agent", "supervisor")
    .add_edge("email_agent", "supervisor")
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
                    "content": "send an email with email_agent using send_email tool with subject 'weather at kathmandu' and body with weather update.",
                }
            ]
        },
        subgraphs=True,
    ):
        pretty_print_messages(chunk, last_message=True)
except Exception as e:
    print(f"Error running supervisor with descriptions: {e}")