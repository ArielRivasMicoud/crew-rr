#!/usr/bin/env python3
"""
Main script to run the CrewAI Research and Reporting application.

This application uses two agents (a Senior Data Researcher and a Reporting Analyst)
to collaboratively research a topic and generate a comprehensive report.
"""

import argparse
import sys
import logging

from src.crew import ResearchCrew
from src.utils.helpers import save_report, check_llm_availability
from src.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run a CrewAI research and reporting process on a given topic.'
    )
    
    parser.add_argument(
        'topic',
        type=str,
        help='The topic to research and report on'
    )
    
    parser.add_argument(
        '--backend',
        type=str,
        choices=['openai', 'ollama'],
        default=settings.DEFAULT_LLM_BACKEND,
        help='The LLM backend to use (default: %(default)s)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Directory to save the output report (default: reports/)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()

def main():
    """Run the CrewAI research and reporting application."""
    args = parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if the selected LLM backend is available
    if not check_llm_availability(args.backend):
        logger.error(f"The selected LLM backend '{args.backend}' is not available.")
        return 1
    
    logger.info(f"Starting research on topic: {args.topic}")
    logger.info(f"Using LLM backend: {args.backend}")
    
    try:
        # Create and run the research crew
        crew = ResearchCrew(backend=args.backend)
        result = crew.run_research(args.topic)
        
        # Save the report
        report_path = save_report(result, args.topic, args.output_dir)
        
        logger.info(f"Research and reporting completed successfully.")
        logger.info(f"Report saved to: {report_path}")
        
        return 0
    
    except Exception as e:
        logger.exception(f"An error occurred during the research process: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 