from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.code_analysis_tools import (
    CodeParserTool, StaticAnalysisTool, SecurityAnalyzerTool, 
    PerformanceAnalyzerTool
)

@CrewBase
class CodeReviewerAgentCrew:
    """Simplified Code Reviewer Agent crew"""

    @agent
    def code_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_reviewer'],
            tools=[CodeParserTool(), StaticAnalysisTool()],
            verbose=True
        )

    @agent
    def security_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['security_specialist'],
            tools=[SecurityAnalyzerTool()],
            verbose=True
        )

    @agent
    def performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['performance_analyst'],
            tools=[PerformanceAnalyzerTool()],
            verbose=True
        )

    @task
    def error_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['error_analysis_task'],
            output_file='output/error_suggestions_report.md'
        )

    @task
    def security_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['security_analysis_task'],
            output_file='output/security_report.md'
        )

    @task
    def performance_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['performance_analysis_task'],
            output_file='output/performance_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the simplified Code Reviewer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )