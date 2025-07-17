"""
Main entry point for the Multi-Agent Supervisor System.

This module provides the main interface for running the multi-agent workflow
with weather and email capabilities.
"""
import os
import sys
from typing import Optional, List
from graph.workflow import execute_workflow, validate_workflow
from tools.timing_tracker import timing_tracker
from utils.messaging import log_agent_activity, format_error_message
from config.constants import validate_config


def setup_environment():
    """Setup environment and validate configuration."""
    try:
        # Try to load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            log_agent_activity("system", "Loaded environment variables from .env file")
        except ImportError:
            log_agent_activity("system", "python-dotenv not installed, using system environment variables")
        
        # Validate configuration
        validate_config()
        log_agent_activity("system", "Configuration validation successful")
        
        return True
        
    except Exception as e:
        print(format_error_message(e, "Environment Setup"))
        return False


def run_single_query(query: str, thread_id: str = "single_query") -> Optional[float]:
    """
    Run a single query through the multi-agent system.
    
    Args:
        query: The user query to process
        thread_id: Unique identifier for this conversation thread
        
    Returns:
        Total execution time in seconds, or None if failed
    """
    print(f"\n{'='*60}")
    print(f"🚀 Processing Query: {query}")
    print('='*60)
    
    # Reset and start timing
    timing_tracker.reset()
    timing_tracker.start_total_timer()
    
    try:
        log_agent_activity("system", "Starting single query execution")
        
        # Execute the workflow
        result = execute_workflow(query, thread_id)
        
        # Display results
        print(f"\n✅ Query processed successfully!")
        print(f"📋 Final task: {result.get('current_task', 'unknown')}")
        print(f"📊 Context: {result.get('context', {})}")
        
        # Show final response messages
        final_messages = result.get('messages', [])
        if final_messages:
            print(f"\n💬 Final Response:")
            for msg in final_messages[-2:]:  # Show last 2 messages
                if hasattr(msg, 'content'):
                    print(f"   {msg.content}")
        
        # Print timing summary
        timing_tracker.print_timing_summary()
        
        return timing_tracker.get_total_time()
        
    except Exception as e:
        print(format_error_message(e, "Query Execution"))
        timing_tracker.print_timing_summary()
        return None


def run_enhanced_examples():
    """Run a comprehensive set of examples demonstrating system capabilities."""
    examples = [
        "What's the weather like in Paris?",
        "Send me an email with subject 'Daily Update' and body 'All systems operational'",
        "Get the weather for Tokyo and email it to me with subject 'Tokyo Weather Report'",
        "Check the weather in London",
        "Email me the weather forecast for New York with subject 'NYC Weather'"
    ]
    
    print("🤖 Multi-Agent Supervisor System - Enhanced Examples")
    print("=" * 70)
    
    successful_runs = 0
    total_time = 0
    
    for i, query in enumerate(examples, 1):
        try:
            execution_time = run_single_query(query, f"example_{i}")
            if execution_time is not None:
                successful_runs += 1
                total_time += execution_time
                print(f"✅ Example {i} completed in {execution_time:.3f}s")
            else:
                print(f"❌ Example {i} failed")
                
        except KeyboardInterrupt:
            print(f"\n⚠️ Execution interrupted by user")
            break
        except Exception as e:
            print(format_error_message(e, f"Example {i}"))
    
    # Summary
    print(f"\n📈 EXECUTION SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful runs: {successful_runs}/{len(examples)}")
    if successful_runs > 0:
        print(f"⏱️ Average execution time: {total_time/successful_runs:.3f}s")
        print(f"🕒 Total execution time: {total_time:.3f}s")


def run_interactive_mode():
    """Run the system in interactive mode for user testing."""
    print("🤖 Multi-Agent Interactive Mode")
    print("=" * 40)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for example queries")
    print()
    
    session_count = 0
    
    while True:
        try:
            # Get user input
            query = input("💬 Enter your query: ").strip()
            
            # Handle special commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif query.lower() in ['help', 'h']:
                print_help()
                continue
            elif not query:
                print("⚠️ Please enter a query")
                continue
            
            # Process the query
            session_count += 1
            run_single_query(query, f"interactive_{session_count}")
            
        except KeyboardInterrupt:
            print(f"\n👋 Goodbye!")
            break
        except Exception as e:
            print(format_error_message(e, "Interactive Mode"))


def print_help():
    """Print help information with example queries."""
    help_text = """
🆘 HELP - Example Queries:

📊 Weather Queries:
  • "What's the weather in Paris?"
  • "Check the weather in London"
  • "Get weather for Tokyo"

📧 Email Queries:
  • "Send me an email with subject 'Test' and body 'Hello world'"
  • "Email me with subject 'Update' and body 'Project status'"

🔄 Combined Queries:
  • "Get weather for NYC and email it to me"
  • "Check weather in Berlin and send it via email with subject 'Weather Report'"

💡 Tips:
  • Be specific about city names for weather
  • Include both subject and body for emails
  • Combined requests will get weather first, then email it
    """
    print(help_text)


def validate_system():
    """Validate that the system is properly configured and ready to run."""
    print("🔍 Validating System Configuration...")
    
    validation_steps = [
        ("Environment Setup", setup_environment),
        ("Workflow Validation", validate_workflow),
    ]
    
    all_valid = True
    
    for step_name, validation_func in validation_steps:
        try:
            result = validation_func()
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {step_name}: {status}")
            if not result:
                all_valid = False
        except Exception as e:
            print(f"  {step_name}: ❌ ERROR - {e}")
            all_valid = False
    
    print(f"\n🎯 System Status: {'✅ READY' if all_valid else '❌ NOT READY'}")
    return all_valid


def main():
    """Main entry point with command line argument handling."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "validate":
            validate_system()
        elif command == "examples":
            if setup_environment():
                run_enhanced_examples()
        elif command == "interactive":
            if setup_environment():
                run_interactive_mode()
        elif command == "query" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            if setup_environment():
                run_single_query(query)
        else:
            print_usage()
    else:
        # Default behavior - run examples
        if setup_environment():
            run_enhanced_examples()


def print_usage():
    """Print usage information."""
    usage_text = """
🚀 Multi-Agent Supervisor System

Usage: python run.py [command] [arguments]

Commands:
  validate      - Validate system configuration
  examples      - Run example queries (default)
  interactive   - Start interactive mode
  query <text>  - Run a specific query

Examples:
  python run.py validate
  python run.py examples
  python run.py interactive
  python run.py query "What's the weather in Paris?"

Environment Setup:
  1. Copy .env-template to .env
  2. Fill in your API keys and email credentials
  3. Run: python run.py validate
    """
    print(usage_text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n👋 System shutdown requested")
    except Exception as e:
        print(format_error_message(e, "System"))
        sys.exit(1) 