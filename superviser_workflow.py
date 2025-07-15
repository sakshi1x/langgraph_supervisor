import smtplib
from email.mime.text import MIMEText
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langchain_core.messages import HumanMessage, SystemMessage
from weather_agent import weather_agent
from email_agent import email_agent


# === LLM Setup ===
llm = ChatOpenAI(
    api_key="ollama",
    model="qwen2.5-coder:32b",
    base_url="",
    temperature=0.1,
    max_tokens=500,
)



# === Supervisor Workflow ===
workflow = create_supervisor(
    [email_agent, weather_agent],
    model=llm,
    prompt=(
        "You are a supervisor agent responsible for delegating tasks to two assistants:\n\n"
        "- `weather_agent`: Handles weather-related queries (e.g., forecasts, current temperature, conditions).\n"
        "- `email_agent`: Handles email-related tasks (e.g., sending emails using subject and body content).\n\n"
        "Your job is to route each task to the correct agent **exactly once** per user request.\n"
        "- Always call `weather_agent` first if weather information is needed, then pass the result to `email_agent` if email delivery is requested.\n"
        "- When the user asks for weather and email, first get weather data from `weather_agent`, then pass that data to `email_agent` with instructions to include the weather details in the email body.\n"
        "- Do not call both agents in parallel.\n"
        "- Do not repeat or reroute the same task to an agent more than once.\n"
        "- Do not perform any work yourself—only delegate.\n\n"
        "For weather + email requests:\n"
        "1. First call `weather_agent` to get weather data\n"
        "2. Then call `email_agent` with the weather data included in the request\n"
        "3. Stop after both tasks are completed.\n\n"
        "Maintain clear, step-by-step task delegation and stop after both tasks are completed."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
)


from langchain_core.messages import convert_to_messages


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
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")
# Compile the workflow
app = workflow.compile()

# === Run Test ===
for chunk in app.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "query",
            }
        ]
    },
):
    pretty_print_messages(chunk, last_message=True)

final_message_history = chunk["supervisor"]["messages"]