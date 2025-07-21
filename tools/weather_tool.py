"""
Weather tool for fetching weather information from OpenWeatherMap API.
"""
import requests
from typing import Dict, Any
from langchain_core.tools import tool
from config.constants import CONFIG, API_ENDPOINTS
from tools.timing_tracker import timing_tracker


@tool
def fetch_weather(city: str) -> str:
    """
    Fetch weather information for a given city.
    
    Args:
        city: The name of the city to get weather information for
        
    Returns:
        A formatted string containing weather information or error message
    """
    timing_tracker.start_timer(f"fetch_weather_{city}")
    
    # Clean the city name
    city = city.strip().strip('"').strip("'")
    
    # Build the API URL
    url = f"{API_ENDPOINTS['openweather']}?q={city}&appid={CONFIG['OPENWEATHER_API_KEY']}&units=metric"
    
    try:
        response = requests.get(url, timeout=CONFIG.get("TIMEOUT_SECONDS", 30))
        response.raise_for_status()
        
        data = response.json()
        
        # Format the weather information
        weather_info = (
            f"Weather in {city}: {data['weather'][0]['description'].title()}, "
            f"Temperature: {data['main']['temp']}°C, "
            f"Humidity: {data['main']['humidity']}%, "
            f"Wind Speed: {data['wind']['speed']} m/s"
        )
        
        print(f"🌤️ [WEATHER] Successfully fetched weather for {city}")
        timing_tracker.stop_timer(f"fetch_weather_{city}")
        return weather_info
        
    except requests.RequestException as e:
        error_msg = f"Error fetching weather for {city}: {str(e)}"
        print(f"❌ [WEATHER] {error_msg}")
        timing_tracker.stop_timer(f"fetch_weather_{city}")
        return error_msg
        
    except KeyError as e:
        error_msg = f"Error parsing weather data for {city}: {str(e)}"
        print(f"❌ [WEATHER] {error_msg}")
        timing_tracker.stop_timer(f"fetch_weather_{city}")
        return error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error fetching weather for {city}: {str(e)}"
        print(f"❌ [WEATHER] {error_msg}")
        timing_tracker.stop_timer(f"fetch_weather_{city}")
        return error_msg


def validate_weather_api() -> bool:
    """
    Validate that the weather API is properly configured.
    
    Returns:
        True if API key is configured, False otherwise
    """
    return bool(CONFIG.get("OPENWEATHER_API_KEY"))


def get_weather_patterns() -> list[str]:
    """
    Get list of weather-related keywords for intent recognition.
    
    Returns:
        List of weather-related keywords
    """
    return [
        'weather', 'temperature', 'forecast', 'climate', 
        'rain', 'sunny', 'cloudy', 'humidity', 'wind'
    ] 