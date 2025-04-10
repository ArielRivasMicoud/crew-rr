"""Tests for agent creation and configuration."""

import unittest
from unittest.mock import patch, MagicMock

from src.agents import ResearcherAgent, AnalystAgent

class TestAgents(unittest.TestCase):
    """Test case for the agents module."""
    
    @patch('src.config.llm_config.get_default_llm')
    def test_researcher_agent_creation(self, mock_get_llm):
        """Test that the researcher agent can be created successfully."""
        # Setup mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create the agent
        agent = ResearcherAgent.create()
        
        # Assert that the agent has the correct properties
        self.assertEqual(agent.role, "Senior Data Researcher")
        self.assertTrue("research" in agent.goal.lower())
        self.assertTrue(agent.verbose)
        self.assertEqual(agent.llm, mock_llm)
    
    @patch('src.config.llm_config.get_default_llm')
    def test_analyst_agent_creation(self, mock_get_llm):
        """Test that the analyst agent can be created successfully."""
        # Setup mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create the agent
        agent = AnalystAgent.create()
        
        # Assert that the agent has the correct properties
        self.assertEqual(agent.role, "Reporting Analyst")
        self.assertTrue("report" in agent.goal.lower())
        self.assertTrue(agent.verbose)
        self.assertEqual(agent.llm, mock_llm)

if __name__ == '__main__':
    unittest.main() 