"""Research tasks for the Senior Data Researcher agent."""

from crewai import Task

def create_research_task(researcher_agent, topic):
    """
    Create a research task for the Senior Data Researcher agent.
    
    Args:
        researcher_agent: The Senior Data Researcher agent
        topic: The topic to research
        
    Returns:
        Task: A research task
    """
    return Task(
        description=f"""
        Research the topic: "{topic}" thoroughly.
        
        Your task is to:
        1. Gather comprehensive information on the topic
        2. Identify key facts, trends, and insights
        3. Find relevant statistics and data points
        4. Analyze the current state and historical context
        5. Identify credible sources and references
        6. Organize your findings in a structured format
        7. Provide a summary of the most important discoveries
        
        Your research should be thorough, accurate, and properly cited.
        The output will be used by the Reporting Analyst to create a comprehensive report.
        """,
        agent=researcher_agent,
        expected_output="""
        A comprehensive research document with the following sections:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Data Points and Statistics
        5. Trends and Patterns
        6. References and Citations
        
        The document should be well-structured, fact-based, and contain all relevant information on the topic.
        """
    ) 