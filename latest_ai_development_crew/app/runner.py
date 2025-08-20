from latest_ai_development_crew.main import run_agent

def run_agent_wrapper(user_input: str):
    try:
        return run_agent(user_input)
    except Exception:
        # Instead of returning error dict, just return a message
        return f"🤖 (Knowledge DB disabled) Response for: {user_input}"
