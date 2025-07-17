"""
Intent analysis utilities for understanding user requests and routing decisions.
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage
from tools.weather_tool import get_weather_patterns
from tools.email_tool import get_email_patterns
from utils.messaging import extract_latest_human_message


def analyze_request_intent(messages: List[BaseMessage]) -> Dict[str, Any]:
    """
    Analyze the conversation to determine what needs to be done.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Dictionary with intent analysis results
    """
    if not messages:
        return {
            "needs_weather": False,
            "needs_email": False,
            "query": "",
            "is_combined": False,
            "confidence": 0.0
        }
    
    # Get the latest query
    latest_query = extract_latest_human_message(messages).lower()
    
    # Get pattern lists
    weather_patterns = get_weather_patterns()
    email_patterns = get_email_patterns()
    
    # Analyze intent patterns
    weather_matches = sum(1 for pattern in weather_patterns if pattern in latest_query)
    email_matches = sum(1 for pattern in email_patterns if pattern in latest_query)
    
    needs_weather = weather_matches > 0
    needs_email = email_matches > 0
    is_combined = needs_weather and needs_email
    
    # Calculate confidence based on number of matches
    total_words = len(latest_query.split())
    confidence = (weather_matches + email_matches) / max(total_words, 1)
    
    return {
        "needs_weather": needs_weather,
        "needs_email": needs_email,
        "query": latest_query,
        "is_combined": is_combined,
        "confidence": min(confidence, 1.0),
        "weather_score": weather_matches,
        "email_score": email_matches
    }


def check_task_completion(messages: List[BaseMessage]) -> Dict[str, bool]:
    """
    Check what tasks have been completed based on conversation history.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Dictionary with completion status for different tasks
    """
    weather_completed = False
    email_completed = False
    task_marked_complete = False
    
    for message in messages:
        if hasattr(message, 'content') and message.content:
            content = str(message.content).lower()
            
            # Check for weather completion - look for weather data with temperature
            if ('weather in' in content and '°c' in content) or \
               ('temperature:' in content and '°c' in content):
                weather_completed = True
                
            # Check for email completion - look for success messages
            if ('email sent successfully' in content or 
                '✅ email sent successfully' in content or
                'email sent' in content):
                email_completed = True
                
            # Check if supervisor marked task complete
            if 'task completed:' in content:
                task_marked_complete = True
    
    return {
        "weather_completed": weather_completed,
        "email_completed": email_completed,
        "task_marked_complete": task_marked_complete,
        "any_completed": weather_completed or email_completed or task_marked_complete
    }


def determine_next_action(
    intent: Dict[str, Any], 
    completion: Dict[str, bool], 
    completed_tasks: List[str]
) -> Dict[str, str]:
    """
    Determine the next action based on intent analysis and completion status.
    
    Args:
        intent: Intent analysis results
        completion: Task completion status
        completed_tasks: List of already completed tasks
        
    Returns:
        Dictionary with next action and reasoning
    """
    # Check completion status using both message analysis and state tracking
    weather_done = completion["weather_completed"] or "weather" in completed_tasks
    email_done = completion["email_completed"] or "email" in completed_tasks
    task_complete = completion["task_marked_complete"]
    
    # Decision logic
    if task_complete:
        return {
            "next_agent": "FINISH",
            "reasoning": "Task has been marked as completed by supervisor"
        }
    
    if intent["needs_weather"] and not weather_done:
        return {
            "next_agent": "weather_specialist",
            "reasoning": "User needs weather information that hasn't been fetched yet"
        }
    
    if intent["needs_email"] and not email_done:
        return {
            "next_agent": "email_specialist",
            "reasoning": "User needs email functionality that hasn't been completed yet"
        }
    
    if intent["is_combined"] and weather_done and not email_done:
        return {
            "next_agent": "email_specialist",
            "reasoning": "Weather data obtained, now need to send email with weather info"
        }
    
    # Check if all requested tasks are done
    if ((intent["needs_weather"] and weather_done and not intent["needs_email"]) or 
        (intent["needs_email"] and email_done and not intent["needs_weather"]) or 
        (intent["is_combined"] and weather_done and email_done)):
        return {
            "next_agent": "FINISH",
            "reasoning": "All requested tasks have been completed successfully"
        }
    
    # Default fallback
    return {
        "next_agent": "FINISH", 
        "reasoning": "No clear next action determined - completing workflow"
    }


def extract_city_from_query(query: str) -> Optional[str]:
    """
    Extract city name from a weather query.
    
    Args:
        query: User query string
        
    Returns:
        City name if found, None otherwise
    """
    import re
    
    # Common patterns for city extraction
    patterns = [
        r'weather (?:in|for) ([A-Za-z\s]+?)(?:\?|$|,)',
        r'weather (?:of|at) ([A-Za-z\s]+?)(?:\?|$|,)',
        r'(?:in|for) ([A-Za-z\s]+?) weather',
        r'([A-Za-z\s]+?) weather'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            # Filter out common words that aren't cities
            stop_words = {'the', 'weather', 'current', 'today', 'now'}
            if city.lower() not in stop_words and len(city) > 1:
                return city
                
    return None


def get_intent_summary(intent: Dict[str, Any], completion: Dict[str, bool]) -> str:
    """
    Create a human-readable summary of intent and completion status.
    
    Args:
        intent: Intent analysis results
        completion: Task completion status
        
    Returns:
        Summary string
    """
    summary_parts = []
    
    # Intent summary
    if intent["is_combined"]:
        summary_parts.append("🎯 Intent: Combined weather + email request")
    elif intent["needs_weather"]:
        summary_parts.append("🎯 Intent: Weather information request")
    elif intent["needs_email"]:
        summary_parts.append("🎯 Intent: Email sending request")
    else:
        summary_parts.append("🎯 Intent: No clear intent detected")
    
    # Completion summary
    status_parts = []
    if completion["weather_completed"]:
        status_parts.append("Weather ✅")
    if completion["email_completed"]:
        status_parts.append("Email ✅")
    if completion["task_marked_complete"]:
        status_parts.append("Task Complete ✅")
        
    if status_parts:
        summary_parts.append(f"📊 Status: {', '.join(status_parts)}")
    else:
        summary_parts.append("📊 Status: No tasks completed yet")
        
    # Confidence
    confidence_pct = intent.get("confidence", 0) * 100
    summary_parts.append(f"🎲 Confidence: {confidence_pct:.1f}%")
    
    return " | ".join(summary_parts) 