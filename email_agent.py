

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

SENDER_EMAIL = ""
SENDER_PASSWORD =  ""
RECEIVER_EMAIL = ""


llm = ChatOpenAI(
    api_key="ollama",
    model="qwen2.5-coder:32b",
    base_url="",
    temperature=0.1,
    max_tokens=500
)

# === Email Sending Tool ===
@tool
def send_email(subject: str, body: str) -> str:
    """Send an email with the given subject and body."""
    try:
        print(f"\n📤 [TOOL CALL] Sending email...\nSubject: {subject}\nBody: {body}")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        success_msg = f"✅ Email sent to {RECEIVER_EMAIL} with subject '{subject}'"
        print(success_msg)
        return success_msg

    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Check your credentials."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {str(e)}"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

# === Email Agent ===
email_agent = create_react_agent(
    model=llm,
    tools=[send_email],
    prompt=(
        "You are an email agent. Use the send_email tool to send emails. "
        "Extract subject and body from requests and call send_email(subject, body). "
        "When weather data is provided in the request, include it in the email body. "
        "Call the tool only once. After calling the tool, return the result to supervisor."
    ),
    name="email_agent",
)