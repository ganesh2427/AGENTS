#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from latest_ai_development_crew.crew import LatestAiDevelopmentCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Agentic Ai',
        'current_year': str(datetime.now().year)
    }
    
    try:
        LatestAiDevelopmentCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")



def run_agent(topic):
    """
    Run the crew with a specific topic from user input.
    """
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year)
    }
    
    try:
        result = LatestAiDevelopmentCrew().crew().kickoff(inputs=inputs)
        return result.raw  # Return the actual result
    except Exception as e:
        return {"error": str(e), "message": "An error occurred while running the crew"}
    


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        LatestAiDevelopmentCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LatestAiDevelopmentCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        LatestAiDevelopmentCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
