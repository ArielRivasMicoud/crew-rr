"""LLM configuration for different backends (OpenAI and Ollama)."""

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from crewai import Agent

from src.config import settings

def get_openai_llm():
    """
    Returns a configured OpenAI LLM instance.
    
    Returns:
        ChatOpenAI: The configured OpenAI LLM instance.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please add it to your .env file.")
    
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=settings.TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )

def get_ollama_llm():
    """
    Returns a configured Ollama LLM instance.
    
    Returns:
        Ollama: The configured Ollama LLM instance.
    """
    return Ollama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE
    )

def get_default_llm():
    """
    Returns the default LLM based on configuration.
    
    Returns:
        Union[ChatOpenAI, Ollama]: The configured LLM instance.
    """
    if settings.DEFAULT_LLM_BACKEND.lower() == 'openai':
        return get_openai_llm()
    elif settings.DEFAULT_LLM_BACKEND.lower() == 'ollama':
        return get_ollama_llm()
    else:
        raise ValueError(f"Unknown LLM backend: {settings.DEFAULT_LLM_BACKEND}")

def configure_agent_llm(agent: Agent, backend: str = None):
    """
    Configure an agent with the specified LLM backend.
    
    Args:
        agent: The CrewAI agent to configure
        backend: The LLM backend to use ('openai' or 'ollama')
        
    Returns:
        Agent: The configured agent
    """
    backend = backend or settings.DEFAULT_LLM_BACKEND
    
    if backend.lower() == 'openai':
        agent.llm = get_openai_llm()
    elif backend.lower() == 'ollama':
        agent.llm = get_ollama_llm()
    else:
        raise ValueError(f"Unknown LLM backend: {backend}")
    
    return agent 