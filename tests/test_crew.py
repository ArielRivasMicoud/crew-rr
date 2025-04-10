"""Tests for the crew functionality."""

import unittest
from unittest.mock import patch, MagicMock

from src.crew import ResearchCrew

class TestCrew(unittest.TestCase):
    """Test case for the crew module."""
    
    @patch('src.config.llm_config.get_openai_llm')
    def test_crew_initialization(self, mock_get_llm):
        """Test that the research crew can be initialized successfully."""
        # Setup mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create the crew
        crew = ResearchCrew(backend="openai")
        
        # Assert that the crew has the correct properties
        self.assertEqual(crew.backend, "openai")
        self.assertIsNone(crew._crew)
    
    @patch('src.config.llm_config.get_openai_llm')
    def test_crew_create(self, mock_get_llm):
        """Test that the research crew can be created successfully."""
        # Setup mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        # Create the crew
        crew = ResearchCrew(backend="openai")
        crew_instance = crew.create_crew()
        
        # Assert that the crew was created and has agents
        self.assertIsNotNone(crew_instance)
        self.assertEqual(len(crew_instance.agents), 2)
        self.assertEqual(crew_instance.process.value, "sequential")

if __name__ == '__main__':
    unittest.main() 