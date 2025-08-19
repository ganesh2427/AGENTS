# src/latest_ai_development/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task,before_kickoff, after_kickoff
#from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class LatestAiDevelopmentCrew():
  """LatestAiDevelopment crew"""

  agents: List[BaseAgent]
  tasks: List[Task]




# adding optional @before_kickoff and @after_kickoff decorators to your crew class. 
# These functions allow you to execute code before and after your crew runs.
# What These Functions Do @before_kickoff: Executes before the crew starts, allowing 
# you to preprocess inputs, set up environment, or load necessary data
# @after_kickoff: Executes after the crew completes, allowing you to post-process results, 
# log outputs, or perform cleanup
  @before_kickoff
  def before_kickoff_function(self, inputs):
    print(f"Before kickoff function with inputs: {inputs}")
    return inputs # You can return the inputs or modify them as needed

  @after_kickoff
  def after_kickoff_function(self, result):
    print(f"After kickoff function with result: {result}")
    return result # You can return the result or modify it as needed
  





  @agent
  def researcher(self) -> Agent:
    return Agent(
      config=self.agents_config['researcher'], # type: ignore[index]
      verbose=True,
      #tools=[SerperDevTool()]
    )

  @agent
  def reporting_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config['reporting_analyst'], # type: ignore[index]
      verbose=True
    )

  @task
  def research_task(self) -> Task:
    return Task(
      config=self.tasks_config['research_task'], # type: ignore[index]
    )

  # @task
  # def reporting_task(self) -> Task:
  #   return Task(
  #     config=self.tasks_config['reporting_task'], # type: ignore[index]
  #     output_file='output/report.md' # This is the file that will be contain the final report.
  #   )

  @task
  def reporting_task(self) -> Task:
      import datetime
      
      timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
      
      return Task(
          config=self.tasks_config['reporting_task'], # type: ignore[index]
          output_file=f'output/{{topic}}_{timestamp}.md'  # Use double braces for topic variable
      )




  @crew
  def crew(self) -> Crew:
    """Creates the LatestAiDevelopment crew"""
    return Crew(
      agents=self.agents, # Automatically created by the @agent decorator
      tasks=self.tasks, # Automatically created by the @task decorator
      process=Process.sequential,
      verbose=True,
    )