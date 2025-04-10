"""Senior Data Researcher agent implementation."""

from crewai import Agent
from src.config.llm_config import get_default_llm

class ResearcherAgent:
    """Senior Data Researcher agent responsible for conducting comprehensive research on topics."""
    
    @staticmethod
    def create(llm=None):
        """
        Create a Senior Data Researcher agent.
        
        Args:
            llm: Optional custom LLM to use for this agent
            
        Returns:
            Agent: Configured Senior Data Researcher agent
        """
        return Agent(
            role="Senior Data Researcher",
            goal="Conduct comprehensive research on the given topic and provide accurate, "
                 "up-to-date information with proper citations",
            backstory="You are an experienced data researcher with expertise in gathering, "
                      "analyzing, and synthesizing information from various sources. You have "
                      "a strong background in academic research, data analysis, and fact-checking. "
                      "You are meticulous and thorough in your approach, always ensuring that "
                      "your research is accurate and well-documented.",
            verbose=True,
            llm=llm or get_default_llm(),
            allow_delegation=True
        ) 