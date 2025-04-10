"""Task definitions for the CrewAI application."""

from src.tasks.research_tasks import create_research_task
from src.tasks.report_tasks import create_report_task

__all__ = ['create_research_task', 'create_report_task'] 