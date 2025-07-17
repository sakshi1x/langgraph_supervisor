import os
import requests
import time
import datetime
from typing import Annotated, Dict, Any, Literal, List
from email.mime.text import MIMEText
import smtplib
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.types import Command, Send
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from typing_extensions import TypedDict

# Set API keys and configurations
OLLAMA_MODEL = "llama3.1:latest"
OLLAMA_BASE_URL = "https://jo3m4y06rnnwhaz.askbhunte.com/v1"
SENDER_EMAIL = "sakshi.nepal@rumsan.net"
SENDER_PASSWORD = "rgrm taap fjmz kilt"
RECEIVER_EMAIL = "nepalsakshi05@gmail.com"
OPENWEATHER_API_KEY = "ca832595840677a6d71622533cc28433"

# ===================== Timing Utilities ===================== #
class TimingTracker:
    """Class to track timing for different components of the system."""
    
    def __init__(self):
        self.timings = {}
        self.start_times = {}
        self.total_start_time = None
        
    def start_total_timer(self):
        """Start the total system timer."""
        self.total_start_time = time.time()
        print(f"⏱️ [TIMING] System started at {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
    def start_timer(self, operation_name: str):
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()
        print(f"⏱️ [TIMING] Started {operation_name} at {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
    def stop_timer(self, operation_name: str):
        """Stop timing an operation and record the duration."""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.timings[operation_name] = duration
            print(f"⏱️ [TIMING] Completed {operation_name} in {duration:.3f} seconds")
            del self.start_times[operation_name]
            return duration
        return None
        
    def get_total_time(self):
        """Get the total system execution time."""
        if self.total_start_time:
            total_time = time.time() - self.total_start_time
            print(f"⏱️ [TIMING] Total system execution time: {total_time:.3f} seconds")
            return total_time
        return None
        
    def print_timing_summary(self):
        """Print a comprehensive timing summary."""
        print(f"\n{'='*60}")
        print(f"⏱️ TIMING SUMMARY")
        print(f"{'='*60}")
        
        total_time = self.get_total_time()
        if total_time:
            print(f"🕒 Total System Time: {total_time:.3f} seconds")
            
        if self.timings:
            print(f"\n📊 Component Breakdown:")
            for operation, duration in sorted(self.timings.items()):
                percentage = (duration / total_time * 100) if total_time else 0
                print(f"   • {operation}: {duration:.3f}s ({percentage:.1f}%)")
                
        print(f"{'='*60}\n")

# Global timing tracker
timing_tracker = TimingTracker()

# Initialize LLM
llm = ChatOpenAI(
    api_key="ollama",
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.4,
)

# Pretty print helper functions
def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=False)
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
        if node_update is None or len(node_update) == 0:
            continue
        print(f"Node: {node_name}")
        pretty_print_message(node_update[-1], indent=True)

# Ensure environment variables are set
os.environ["OPENWEATHER_API_KEY"] = OPENWEATHER_API_KEY

# Enhanced State Management
class SupervisorState(TypedDict):
    messages: List
    next: str
    current_task: str
    completed_tasks: List[str]
    context: Dict[str, Any]

# ===================== Core Tools ===================== #
@tool
def fetch_weather(city: str) -> str:
    """Fetch weather information for a given city."""
    timing_tracker.start_timer(f"fetch_weather_{city}")
    
    city = city.strip().strip('"').strip("'")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
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

@tool
def send_email(subject: str, body: str) -> str:
    """Send an email with the given subject and body."""
    timing_tracker.start_timer("send_email")
    
    try:
        print(f"📤 [EMAIL] Sending email with subject: {subject}")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        success_msg = f"✅ Email sent successfully to {RECEIVER_EMAIL}"
        print(f"📤 [EMAIL] {success_msg}")
        timing_tracker.stop_timer("send_email")
        return success_msg
    except smtplib.SMTPAuthenticationError:
        error_msg = "❌ Email authentication failed. Check your email credentials."
        print(f"📤 [EMAIL] {error_msg}")
        timing_tracker.stop_timer("send_email")
        return error_msg
    except Exception as e:
        error_msg = f"❌ Error sending email: {str(e)}"
        print(f"📤 [EMAIL] {error_msg}")
        timing_tracker.stop_timer("send_email")
        return error_msg

# ===================== Handoff Tools ===================== #
@tool
def handoff_to_weather(task_description: str = "Handle weather-related requests") -> str:
    """Transfer control to the weather specialist agent."""
    return f"🌤️ Transferring to weather agent: {task_description}"

@tool
def handoff_to_email(task_description: str = "Handle email-related requests") -> str:
    """Transfer control to the email specialist agent."""
    return f"📧 Transferring to email agent: {task_description}"

@tool
def complete_task(summary: str) -> str:
    """Mark the current task as completed with a summary."""
    return f"✅ Task completed: {summary}"

# ===================== Agent Creation ===================== #
def create_agent(llm, tools, name, system_prompt):
    """Create a reactive agent with given tools and prompt."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    agent = create_react_agent(model=llm, tools=tools, prompt=prompt)
    agent.name = name
    return agent

# Create specialized agents with stronger prompts
weather_agent = create_agent(
    llm, 
    [fetch_weather],
    "weather_specialist",
    """You are a weather specialist. Your role is to:
    1. Fetch accurate weather information for requested cities using the fetch_weather tool
    2. Provide clear, well-formatted weather summaries
    3. Handle weather-related queries professionally
    
    Always use the fetch_weather tool to get current weather data.
    Format your responses clearly and include all relevant weather information."""
)

email_agent = create_agent(
    llm, 
    [send_email],
    "email_specialist", 
    """You are an email specialist. You MUST use the send_email tool for any email request.

    CRITICAL RULES:
    1. ALWAYS call the send_email tool - never just describe what you would do
    2. Extract weather data from conversation history when needed
    3. Create professional email subjects and bodies
    
    For weather emails:
    - Look through conversation messages for weather data (temperature, conditions, etc.)
    - Include all weather details in the email body
    - Use the exact subject requested by the user
    
    NEVER just say you sent an email - you MUST actually call the send_email tool with proper subject and body parameters.
    
    If you see weather information in the conversation, extract it and format it nicely in the email body."""
)

# Create supervisor agent with handoff tools
supervisor_agent = create_agent(
    llm,
    [handoff_to_weather, handoff_to_email, complete_task],
    "supervisor",
    """You are a multi-agent supervisor coordinating weather and email specialists.

    RESPONSIBILITIES:
    - Analyze user requests to determine which specialist(s) are needed
    - Route tasks to appropriate agents using handoff tools
    - Coordinate multi-step workflows (e.g., get weather then email it)
    - Determine when all tasks are completed

    ROUTING RULES:
    - For weather requests: use handoff_to_weather tool
    - For email requests: use handoff_to_email tool  
    - For combined requests: coordinate both agents in sequence
    - When all tasks done: use complete_task tool

    HANDOFF TOOL USAGE:
    - Include clear task descriptions when using handoff tools
    - Monitor conversation for task completion
    - Only use complete_task when user's request is fully satisfied
    
    Always think step-by-step about what the user needs and route accordingly."""
)

# ===================== Enhanced Routing Logic ===================== #
class RouterDecision(TypedDict):
    next_agent: Literal["weather_specialist", "email_specialist", "supervisor", "FINISH"]
    reasoning: str
    task_description: str

def analyze_request_intent(messages: List) -> Dict[str, Any]:
    """Analyze the conversation to determine what needs to be done."""
    if not messages:
        return {"needs_weather": False, "needs_email": False, "query": ""}
    
    # Get the latest human message
    latest_query = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            latest_query = msg.content.lower()
            break
    
    # Analyze intent patterns
    weather_patterns = [
        'weather', 'temperature', 'forecast', 'climate', 'rain', 'sunny', 'cloudy'
    ]
    email_patterns = [
        'email', 'send', 'mail', 'notify', 'message', 'inform'
    ]
    
    needs_weather = any(pattern in latest_query for pattern in weather_patterns)
    needs_email = any(pattern in latest_query for pattern in email_patterns)
    
    return {
        "needs_weather": needs_weather,
        "needs_email": needs_email,
        "query": latest_query,
        "is_combined": needs_weather and needs_email
    }

def check_task_completion(messages: List) -> Dict[str, bool]:
    """Check what tasks have been completed based on conversation history."""
    weather_completed = False
    email_completed = False
    task_marked_complete = False
    
    for msg in messages:
        if hasattr(msg, 'content') and msg.content:
            content = str(msg.content).lower()
            # Check for weather completion - look for weather data with temperature
            if ('weather in' in content and '°c' in content) or ('temperature:' in content and '°c' in content):
                weather_completed = True
            # Check for email completion - look for success messages (including tool execution logs)
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
        "task_marked_complete": task_marked_complete
    }

# ===================== Agent Nodes ===================== #
def weather_node(state: SupervisorState):
    """Weather specialist node."""
    timing_tracker.start_timer("weather_agent_processing")
    print("🌤️ [WEATHER NODE] Processing weather request...")
    
    result = weather_agent.invoke(state)
    new_messages = result["messages"]
    
    timing_tracker.stop_timer("weather_agent_processing")
    
    # Mark weather as completed in context
    return Command(
        update={
            "messages": state["messages"] + [new_messages[-1]],
            "current_task": "weather_completed",
            "context": {**state.get("context", {}), "weather_processed": True},
            "completed_tasks": state.get("completed_tasks", []) + ["weather"]
        },
        goto="supervisor"
    )

def email_node(state: SupervisorState):
    """Email specialist node."""
    timing_tracker.start_timer("email_agent_processing")
    print("📧 [EMAIL NODE] Processing email request...")
    print(f"📧 [EMAIL NODE] Current messages in conversation: {len(state['messages'])}")
    
    # Debug: Show recent messages to understand context
    recent_messages = state["messages"][-3:] if len(state["messages"]) >= 3 else state["messages"]
    for i, msg in enumerate(recent_messages):
        if hasattr(msg, 'content'):
            print(f"📧 [EMAIL NODE] Message {i}: {msg.content[:100]}...")
    
    result = email_agent.invoke(state)
    new_messages = result["messages"]
    
    print(f"📧 [EMAIL NODE] Agent returned {len(new_messages)} messages")
    if new_messages:
        print(f"📧 [EMAIL NODE] Last agent response: {new_messages[-1].content[:200]}...")
    
    # Check if send_email was actually called by looking for the success message
    email_actually_sent = False
    for msg in new_messages:
        if hasattr(msg, 'content') and msg.content:
            if "✅ Email sent successfully" in msg.content:
                email_actually_sent = True
                break
    
    if not email_actually_sent:
        print("⚠️ [EMAIL NODE] Warning: send_email tool may not have been called!")
        # Try to force the agent to use the tool by adding a clarifying message
        force_message = HumanMessage(content="Please actually use the send_email tool now to send the email. Do not just describe what you would do.")
        retry_state = {
            **state,
            "messages": state["messages"] + [force_message]
        }
        retry_result = email_agent.invoke(retry_state)
        new_messages = retry_result["messages"]
        print(f"📧 [EMAIL NODE] Retry result: {new_messages[-1].content[:200]}...")
    
    timing_tracker.stop_timer("email_agent_processing")
    
    # Mark email as completed in context
    return Command(
        update={
            "messages": state["messages"] + [new_messages[-1]],
            "current_task": "email_completed", 
            "context": {**state.get("context", {}), "email_processed": True},
            "completed_tasks": state.get("completed_tasks", []) + ["email"]
        },
        goto="supervisor"
    )

def supervisor_node(state: SupervisorState):
    """Enhanced supervisor node with reliable routing."""
    timing_tracker.start_timer("supervisor_routing")
    print("🧠 [SUPERVISOR] Analyzing request and routing...")
    
    # Analyze what the user needs
    intent = analyze_request_intent(state["messages"])
    completion = check_task_completion(state["messages"])
    completed_tasks = state.get("completed_tasks", [])
    
    print(f"🧠 [SUPERVISOR] Intent analysis: {intent}")
    print(f"🧠 [SUPERVISOR] Completion status: {completion}")
    print(f"🧠 [SUPERVISOR] Completed tasks: {completed_tasks}")
    
    # Enhanced completion logic using both message analysis and state tracking
    weather_done = completion["weather_completed"] or "weather" in completed_tasks
    email_done = completion["email_completed"] or "email" in completed_tasks
    task_complete = completion["task_marked_complete"]
    
    # Determine routing based on intent and completion
    if task_complete:
        next_agent = "FINISH"
        reasoning = "Task has been marked as completed by supervisor"
        
    elif intent["needs_weather"] and not weather_done:
        next_agent = "weather_specialist"
        reasoning = "User needs weather information that hasn't been fetched yet"
        
    elif intent["needs_email"] and not email_done:
        next_agent = "email_specialist"  
        reasoning = "User needs email functionality that hasn't been completed yet"
        
    elif intent["is_combined"] and weather_done and not email_done:
        next_agent = "email_specialist"
        reasoning = "Weather data obtained, now need to send email with weather info"
        
    elif (intent["needs_weather"] and weather_done and not intent["needs_email"]) or \
         (intent["needs_email"] and email_done and not intent["needs_weather"]) or \
         (intent["is_combined"] and weather_done and email_done):
        next_agent = "FINISH"
        reasoning = "All requested tasks have been completed successfully"
        
    else:
        # Let supervisor agent make the final decision
        try:
            result = supervisor_agent.invoke(state)
            supervisor_response = result["messages"][-1]
            
            # Check if supervisor used a handoff tool or completion tool
            response_lower = supervisor_response.content.lower()
            if "transferring to weather agent" in response_lower:
                next_agent = "weather_specialist"
                reasoning = "Supervisor determined weather specialist is needed"
            elif "transferring to email agent" in response_lower:
                next_agent = "email_specialist"
                reasoning = "Supervisor determined email specialist is needed"
            elif "task completed:" in response_lower:
                next_agent = "FINISH"
                reasoning = "Supervisor marked task as completed"
            else:
                next_agent = "FINISH"
                reasoning = "Supervisor completed analysis - finishing workflow"
            
            # Add supervisor's response to messages
            state = {
                **state,
                "messages": state["messages"] + [supervisor_response]
            }
        except Exception as e:
            print(f"⚠️ [SUPERVISOR] Agent decision failed, using fallback: {e}")
            next_agent = "FINISH"
            reasoning = "Fallback decision due to supervisor agent error"
    
    print(f"🧠 [SUPERVISOR] Routing to: {next_agent}")
    print(f"🧠 [SUPERVISOR] Reasoning: {reasoning}")
    
    timing_tracker.stop_timer("supervisor_routing")
    
    if next_agent == "FINISH":
        next_agent = END
    
    return Command(
        update={
            "next": next_agent,
            "current_task": f"routing_to_{next_agent}",
            **state
        },
        goto=next_agent
    )

# ===================== Graph Construction ===================== #
def create_supervisor_workflow():
    """Create the enhanced supervisor workflow."""
    builder = StateGraph(SupervisorState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("weather_specialist", weather_node)
    builder.add_node("email_specialist", email_node)
    
    # Set entry point
    builder.add_edge(START, "supervisor")
    
    return builder

# Build the graph
workflow_builder = create_supervisor_workflow()
graph = workflow_builder.compile()

# ===================== Enhanced Example Usage ===================== #
def run_enhanced_examples():
    """Run examples with the enhanced supervisor system."""
    examples = [
        "What's the weather like in Paris?",
        "Send me an email with subject 'Daily Update' and body 'All systems operational'",
        "Get the weather for Tokyo and email it to me with subject 'Tokyo Weather Report'"
    ]
    
    for i, query in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"🚀 Example {i}: {query}")
        print('='*60)
        
        # Reset timing tracker for each example
        global timing_tracker
        timing_tracker = TimingTracker()
        timing_tracker.start_total_timer()
        
        initial_state = {
            'messages': [HumanMessage(content=query)],
            'next': '',
            'current_task': 'initializing',
            'completed_tasks': [],
            'context': {}
        }
        
        config = {
            "configurable": {
                "thread_id": f"enhanced_example_{i}",
                "recursion_limit": 10  # Reduced from 20 to prevent excessive loops
            }
        }
        
        try:
            timing_tracker.start_timer("workflow_execution")
            print("🎯 Starting enhanced supervisor workflow...")
            result = graph.invoke(input=initial_state, config=config)
            timing_tracker.stop_timer("workflow_execution")
            
            print(f"\n✅ Workflow completed successfully!")
            print(f"📋 Final task: {result.get('current_task', 'unknown')}")
            print(f"📊 Context: {result.get('context', {})}")
            
            # Print the final response
            final_messages = result.get('messages', [])
            if final_messages:
                print(f"\n💬 Final Response:")
                for msg in final_messages[-2:]:  # Show last 2 messages
                    if hasattr(msg, 'content'):
                        print(f"   {msg.content}")
            
            # Print timing summary for this example
            timing_tracker.print_timing_summary()
                        
        except Exception as e:
            print(f"❌ Error in enhanced workflow: {e}")
            timing_tracker.print_timing_summary()
            import traceback
            traceback.print_exc()

def run_single_query(query: str):
    """Run a single query with timing measurements."""
    print(f"\n{'='*60}")
    print(f"🚀 Single Query Test: {query}")
    print('='*60)
    
    # Reset timing tracker
    global timing_tracker
    timing_tracker = TimingTracker()
    timing_tracker.start_total_timer()
    
    initial_state = {
        'messages': [HumanMessage(content=query)],
        'next': '',
        'current_task': 'initializing',
        'completed_tasks': [],
        'context': {}
    }
    
    config = {
        "configurable": {
            "thread_id": "single_query_test",
            "recursion_limit": 10
        }
    }
    
    try:
        timing_tracker.start_timer("workflow_execution")
        print("🎯 Starting supervisor workflow...")
        result = graph.invoke(input=initial_state, config=config)
        timing_tracker.stop_timer("workflow_execution")
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"📋 Final task: {result.get('current_task', 'unknown')}")
        
        # Print the final response
        final_messages = result.get('messages', [])
        if final_messages:
            print(f"\n💬 Final Response:")
            for msg in final_messages[-2:]:
                if hasattr(msg, 'content'):
                    print(f"   {msg.content}")
        
        # Print timing summary
        timing_tracker.print_timing_summary()
        
        return timing_tracker.get_total_time()
                    
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        timing_tracker.print_timing_summary()
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🤖 LangGraph Multi-Agent Supervisor - Enhanced Implementation with Timing")
    print("=" * 70)
    
    # You can uncomment the line below to run all examples
    run_enhanced_examples()
    
    # Or test with a single query like this:
    # run_single_query("What's the weather like in London?")
