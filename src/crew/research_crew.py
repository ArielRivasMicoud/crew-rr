"""Research crew implementation that manages the collaboration between agents."""

from crewai import Crew, Process

from src.agents import ResearcherAgent, AnalystAgent
from src.tasks import create_research_task, create_report_task
from src.config.llm_config import get_openai_llm, get_ollama_llm

class ResearchCrew:
    """Research crew that manages the collaboration between researcher and analyst agents."""
    
    def __init__(self, backend="openai"):
        """
        Initialize the research crew.
        
        Args:
            backend: The LLM backend to use ('openai' or 'ollama')
        """
        self.backend = backend
        self._researcher = None
        self._analyst = None
        self._crew = None
    
    @property
    def researcher(self):
        """Get the researcher agent, initializing it if necessary."""
        if self._researcher is None:
            llm = get_openai_llm() if self.backend == "openai" else get_ollama_llm()
            self._researcher = ResearcherAgent.create(llm=llm)
        return self._researcher
    
    @property
    def analyst(self):
        """Get the analyst agent, initializing it if necessary."""
        if self._analyst is None:
            llm = get_openai_llm() if self.backend == "openai" else get_ollama_llm()
            self._analyst = AnalystAgent.create(llm=llm)
        return self._analyst
    
    def create_crew(self):
        """
        Create the research crew with the researcher and analyst agents.
        
        Returns:
            Crew: A CrewAI crew with the configured agents
        """
        self._crew = Crew(
            agents=[self.researcher, self.analyst],
            tasks=[],  # Tasks will be added when running the research
            verbose=True,
            process=Process.sequential  # Tasks will run in sequence
        )
        return self._crew
    
    def run_research(self, topic):
        """
        Run the research process on a given topic.
        
        Args:
            topic: The topic to research
            
        Returns:
            str: The final report
        """
        # Create the crew if it doesn't exist
        if self._crew is None:
            self.create_crew()
        
        # Create the research task
        research_task = create_research_task(self.researcher, topic)
        
        # Create the report task using the research task
        report_task = create_report_task(self.analyst, research_task)
        
        # Add tasks to the crew
        self._crew.tasks = [research_task, report_task]
        
        # Run the crew and return the result
        result = self._crew.kickoff()
        return result 