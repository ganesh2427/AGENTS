# crewai_agent.py
import os
import sys
from datetime import datetime

# Make sure we can import from src/
ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT, "src"))

from latest_ai_development_crew.crew import LatestAiDevelopmentCrew

def respond(prompt: str) -> str:
    """
    Run the CrewAI pipeline with the given user prompt as 'topic'.
    Returns the result as a string.
    """

    # Build inputs for your crew
    inputs = {
        "topic": prompt,
        "current_year": str(datetime.now().year)
    }

    # Instantiate and run
    crew = LatestAiDevelopmentCrew().crew()
    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        return f"[Error while running CrewAI: {e}]"

    # Some Crew implementations write to file, but we’ll return string
    return str(result)
