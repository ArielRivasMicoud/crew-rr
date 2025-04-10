"""Reporting tasks for the Reporting Analyst agent."""

from crewai import Task

def create_report_task(analyst_agent, research_task):
    """
    Create a report creation task for the Reporting Analyst agent.
    
    Args:
        analyst_agent: The Reporting Analyst agent
        research_task: The completed research task with results
        
    Returns:
        Task: A report creation task
    """
    return Task(
        description=f"""
        Create a comprehensive report based on the research findings provided by the Senior Data Researcher.
        
        Your task is to:
        1. Review and analyze the research findings
        2. Identify the most important insights and key takeaways
        3. Structure the information in a logical and coherent manner
        4. Create a narrative that explains the significance of the findings
        5. Develop clear, concise sections with appropriate headings
        6. Include relevant data visualizations (described textually)
        7. Provide actionable recommendations based on the insights
        8. Ensure the report is accessible to both technical and non-technical audiences
        
        The research findings are as follows:
        {research_task.output}
        """,
        agent=analyst_agent,
        expected_output="""
        A comprehensive report with the following sections:
        1. Executive Summary
        2. Introduction
        3. Methodology
        4. Key Findings and Insights
        5. Detailed Analysis
        6. Data Visualization Suggestions
        7. Implications
        8. Recommendations
        9. Conclusion
        10. References
        
        The report should be well-structured, insightful, and actionable, with a clear narrative that explains the significance of the findings.
        """
    )

def write_comprehensive_report(
    topic: str, 
    research_data: str, 
    industry_trends: str,
    expert_opinions: str
) -> str:
    """
    Write a comprehensive, well-structured research report based on collected information.
    
    Args:
        topic: The research topic
        research_data: Collected research data
        industry_trends: Information on industry trends
        expert_opinions: Expert opinions on the topic
        
    Returns:
        A comprehensive markdown report
    """
    # ADD TO THE SYSTEM MESSAGE EXPLICIT INSTRUCTIONS TO USE PROPER MARKDOWN FORMATTING
    system_message = f"""
    You are a professional research report writer tasked with creating a comprehensive
    markdown report on {topic}.
    
    CRITICAL FORMATTING INSTRUCTIONS - FOLLOW EXACTLY:
    You MUST format sections EXACTLY as shown in these examples:
    
    # Research Report: {topic}
    
    *Generated on: 2023-04-10 14:30:00*
    
    ## Executive Summary
    
    This is the executive summary content...
    
    ## Introduction
    
    Introduction content goes here...
    
    ## Key Findings and Insights
    
    ### Finding One
    
    Content about finding one...
    
    ### Finding Two
    
    Content about finding two...
    
    ## Detailed Analysis
    
    ### Subtopic One
    
    Analysis of subtopic one...
    
    ### Subtopic Two
    
    Analysis of subtopic two...
    
    ## Data Visualization Suggestions
    
    ### Growth Trend Visualization
    
    A line chart showing growth trends over time...
    
    ### Comparison Visualization
    
    A bar chart comparing metrics before and after implementation...
    
    ## Recommendations
    
    ### Recommendation One
    
    Details about recommendation one...
    
    ### Recommendation Two
    
    Details about recommendation two...
    
    ## References
    
    ### Author, A. (Year)
    
    *Title of the work*. Publisher information.
    
    ### Author, B. & Author, C. (Year)
    
    Title of the article. *Journal Name*, volume(issue), page range.
    
    IMPORTANT RULES:
    1. NEVER use "**Section Title:**" or numbered formats like "1. Section Title:"
    2. ALWAYS use "## " (double hash) for main section headers
    3. ALWAYS use "### " (triple hash) for ALL subsections, including individual references
    4. NEVER use bullet points with "- **Title:**" format for any content
    5. Main sections MUST be formatted with "## " exactly as shown
    6. ALWAYS format each reference as a separate subsection with "### " followed by the author and year
    
    Your report MUST include these exact section formats in this order:
    1. Title (format: '# Research Report: {topic}')
    2. Generation date (format: '*Generated on: YYYY-MM-DD HH:MM:SS*')
    3. Executive Summary (format: '## Executive Summary')
    4. Introduction (format: '## Introduction')
    5. Methodology (format: '## Methodology')
    6. Key Findings and Insights (format: '## Key Findings and Insights')
    7. Detailed Analysis (format: '## Detailed Analysis')
    8. Data Visualization Suggestions (format: '## Data Visualization Suggestions')
    9. Implications (format: '## Implications')
    10. Recommendations (format: '## Recommendations')
    11. Conclusion (format: '## Conclusion')
    12. References (format: '## References' with each reference as '### Author (Year)')
    
    Use the provided research data, industry trends, and expert opinions to create
    a factual, insightful, and well-structured report.
    """
    
    # FORMAT THE USER MESSAGE TO INCLUDE CONTEXT AND INSTRUCTIONS
    user_message = f"""
    Please write a comprehensive research report on {topic}.
    
    Use the following research data:
    {research_data}
    
    Industry trends information:
    {industry_trends}
    
    Expert opinions:
    {expert_opinions}
    
    Follow the formatting instructions exactly to ensure proper rendering of the report.
    """
    
    # Generate the report using the LLM
    result = get_llm_response(system_message, user_message)
    if result is None:
        return "Error generating report. Please try again."
    
    return result

def get_llm_response(system_message: str, user_message: str) -> str:
    """
    Get a response from the LLM using the system and user messages.
    
    Args:
        system_message: The system message to send to the LLM
        user_message: The user message to send to the LLM
        
    Returns:
        The LLM's response as a string
    """
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    import os
    
    # Initialize the ChatOpenAI instance
    llm = ChatOpenAI(
        model_name=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY", "")
    )
    
    # Create the messages
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_message)
    ]
    
    # Get the response
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return None 