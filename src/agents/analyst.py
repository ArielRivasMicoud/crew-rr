"""Reporting Analyst agent implementation."""

from crewai import Agent
from src.config.llm_config import get_default_llm

class AnalystAgent:
    """Reporting Analyst agent responsible for creating well-structured reports based on research data."""
    
    @staticmethod
    def create(llm=None):
        """
        Create a Reporting Analyst agent.
        
        Args:
            llm: Optional custom LLM to use for this agent
            
        Returns:
            Agent: Configured Reporting Analyst agent
        """
        return Agent(
            role="Reporting Analyst",
            goal="Create comprehensive, well-structured reports based on research findings "
                 "that are clear, insightful, and actionable",
            backstory="You are an expert reporting analyst with a talent for transforming "
                      "complex research data into clear, compelling reports. You have "
                      "exceptional skills in data visualization, narrative structure, and "
                      "communication. You excel at identifying key insights and presenting "
                      "them in a way that is accessible to various audiences while maintaining "
                      "accuracy and depth.",
            verbose=True,
            llm=llm or get_default_llm(),
            allow_delegation=True
        ) 