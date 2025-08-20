import os
import logging

logger = logging.getLogger(__name__)

try:
    # Force disable knowledge if running on Streamlit Cloud
    os.environ["CREWAI_DISABLE_KNOWLEDGE"] = "true"

    from latest_ai_development_crew.main import run_agent

except Exception as e:
    logger.error(f"Failed to import CrewAI agent. Falling back. Error: {e}")

    def run_agent(user_input: str):
        """
        Fallback runner if CrewAI or chromadb fails.
        """
        return {
            "error": "CrewAI with chromadb could not be initialized.",
            "message": "Running in fallback mode. Knowledge features are disabled.",
            "input": user_input,
        }


def run_agent_wrapper(user_input: str):
    """
    Wrapper for Streamlit to safely run agent.
    """
    try:
        result = run_agent(user_input)
        # Ensure result is string for Streamlit display
        return str(result)
    except Exception as e:
        logger.exception("Error running agent")
        return f"⚠️ Agent failed: {e}"
