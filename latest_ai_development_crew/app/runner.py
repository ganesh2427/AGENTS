import sys
import os

# Add src folder to Python path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from latest_ai_development_crew.main import run_agent

def run_agent_wrapper(user_input: str):
    """
    Wrapper around the original run_agent function in src/latest_ai_development_crew/main.py
    """
    return run_agent(user_input)
