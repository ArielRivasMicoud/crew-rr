"""Global application settings loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Default LLM backend
DEFAULT_LLM_BACKEND = os.getenv('DEFAULT_LLM_BACKEND', 'openai')  # 'openai' or 'ollama'

# Agent Configuration
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '3')) 