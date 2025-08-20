# import sys
# import os

# # Add project root to path
# project_root = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, os.path.join(project_root, 'src'))

# from latest_ai_development_crew.main import run_agent

# def run_agent_wrapper(user_input):
#     return run_agent(user_input)

import sys
import types

# ---- Patch chromadb before crewai tries to import it ----
try:
    import chromadb
except Exception:
    # Create a fake chromadb module so crewai won't crash
    fake_chromadb = types.ModuleType("chromadb")
    fake_chromadb.Client = lambda *args, **kwargs: None
    fake_chromadb.__version__ = "0.0.0"
    sys.modules["chromadb"] = fake_chromadb

# Now safely import your main runner
from latest_ai_development_crew.main import run_agent


def run_agent_wrapper(user_input: str):
    try:
        result = run_agent(user_input)

        if isinstance(result, dict) and "error" in result:
            return f"🤖 {result.get('message', 'Knowledge DB disabled')} \n\nResponse for: {user_input}"

        return result

    except Exception as e:
        return f"🤖 (Safe Mode) Unable to use Knowledge DB. Response for: {user_input}"

