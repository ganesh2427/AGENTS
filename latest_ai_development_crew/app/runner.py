import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from latest_ai_development_crew.main import run_agent

def run_agent_wrapper(user_input):
    return run_agent(user_input)