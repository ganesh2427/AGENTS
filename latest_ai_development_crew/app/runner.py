# import sys
# import os

# # Add project root to path
# project_root = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, os.path.join(project_root, 'src'))

# from latest_ai_development_crew.main import run_agent

# def run_agent_wrapper(user_input):
#     return run_agent(user_input)


from latest_ai_development_crew.main import run_agent

def run_agent_wrapper(user_input: str):
    try:
        result = run_agent(user_input)

        # If CrewAI returned a dict with an "error" key, clean it up
        if isinstance(result, dict) and "error" in result:
            return f"🤖 {result.get('message', 'Knowledge DB disabled')} \n\nResponse for: {user_input}"

        return result

    except Exception as e:
        # Last-resort fallback if something else breaks
        return f"🤖 (Safe Mode) Unable to use Knowledge DB. Response for: {user_input}"
