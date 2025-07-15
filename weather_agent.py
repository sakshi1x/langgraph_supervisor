# weather_agent.py

import os
import requests
from typing import Annotated
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Environment
os.environ["OPENWEATHER_API_KEY"] = ""

# === LLM Model Setup ===
llm = ChatOpenAI(
    api_key="ollama",
    model="qwen2.5-coder:32b",
    base_url="",
    temperature=0.1,
    max_tokens=500
)

@tool
def fetch_weather(city: str) -> dict:
    """Fetch weather information for a given city."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    city = city.strip().strip('"').strip("'")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {"status": "success",
        "data": {
            "weather": data['weather'][0]['description'].title(),
            "temperature": f"{data['main']['temp']}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
        }
    }
        
    except requests.RequestException as e:
        return {"error": f"Error fetching weather for {city}: {str(e)}"}
    except KeyError as e:
        return {"error": f"Error parsing weather data for {city}: {str(e)}"}

from langchain.agents import tool
from langchain_core.messages import AIMessage



weather_tools = [fetch_weather]

weather_agent = create_react_agent(
    model=llm,
    tools=weather_tools,
    prompt="""You are a weather agent . Your only job is to fetch data using fetch_weather tool . """,
    name="weather_agent"
)