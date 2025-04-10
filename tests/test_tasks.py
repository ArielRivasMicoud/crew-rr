"""Tests for the tasks functionality."""

import unittest
from unittest.mock import patch, MagicMock

from src.tasks import create_research_task, create_report_task
from src.agents import ResearcherAgent, AnalystAgent

class TestTasks(unittest.TestCase):
    """Test case for the tasks module."""
    
    @patch('src.config.llm_config.get_default_llm')
    def test_create_research_task(self, mock_get_llm):
        """Test that a research task can be created successfully."""
        # Setup mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create an agent and task
        agent = ResearcherAgent.create()
        task = create_research_task(agent, "Test Topic")
        
        # Assert that the task has the correct properties
        self.assertEqual(task.agent, agent)
        self.assertTrue("Test Topic" in task.description)
        self.assertTrue("Executive Summary" in task.expected_output)
    
    @patch('src.config.llm_config.get_default_llm')
    def test_create_report_task(self, mock_get_llm):
        """Test that a report task can be created successfully."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create an agent and task
        agent = AnalystAgent.create()
        research_task = MagicMock()
        research_task.output = "Research findings"
        
        task = create_report_task(agent, research_task)
        
        # Assert that the task has the correct properties
        self.assertEqual(task.agent, agent)
        self.assertTrue("Research findings" in task.description)
        self.assertTrue("Executive Summary" in task.expected_output)

if __name__ == '__main__':
    unittest.main() 