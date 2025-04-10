# Deployment Guide for CrewAI Research and Reporting Application

This guide outlines the steps to deploy and run the CrewAI Research and Reporting application in different environments.

## Local Development Deployment

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)
- OpenAI API key (for OpenAI backend)
- Ollama installed (for local LLM backend)

### Quick Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd crewAi/rr
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```
   This script will:
   - Create a virtual environment
   - Install dependencies
   - Set up environment files
   - Create necessary directories
   - Make scripts executable

3. **Configure environment variables**
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

4. **Run the application**
   ```bash
   source venv/bin/activate
   ./main.py "Your research topic"
   ```

### Manual Setup (Alternative)

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p reports/openai reports/ollama
   ```

5. **Run the application**
   ```bash
   python main.py "Your research topic"
   ```

## Server Deployment

### Prerequisites
- Linux server (Ubuntu 20.04 or similar recommended)
- Python 3.8 or higher
- pip (Python package manager)
- Screen or tmux (for running processes in the background)
- OpenAI API key (for OpenAI backend)
- Ollama installed (for local LLM backend)

### Setup Steps

1. **Connect to your server**
   ```bash
   ssh username@server-ip
   ```

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git
   ```

3. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crewAi/rr
   ```

4. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

5. **Configure environment variables**
   ```bash
   # Edit .env file with your API keys
   nano .env
   ```

6. **Run in a persistent session using Screen**
   ```bash
   screen -S crewai
   source venv/bin/activate
   ./main.py "Your research topic"
   ```
   
   Press `Ctrl+A` then `D` to detach from the screen session.
   To reattach later, use `screen -r crewai`.

## Docker Deployment (Future)

*Note: This section is a roadmap for future implementation*

1. **Create a Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "main.py"]
   ```

2. **Build the Docker image**
   ```bash
   docker build -t crewai-research .
   ```

3. **Run the container**
   ```bash
   docker run -e OPENAI_API_KEY=your_key_here crewai-research "Your research topic"
   ```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Errors**
   - Ensure your API key is correctly set in the `.env` file
   - Check that the API key has not expired or reached its usage limit
   - Verify you have billing set up on your OpenAI account

2. **Ollama Connection Issues**
   - Make sure Ollama is running: `ollama serve`
   - Verify you have pulled the model you're trying to use: `ollama pull llama3`
   - Check the Ollama URL in your `.env` file

3. **Package Installation Problems**
   - Try upgrading pip: `pip install --upgrade pip`
   - If you encounter issues with specific packages, try installing them individually

4. **Permission Errors**
   - Ensure script files are executable: `chmod +x main.py example.py setup.sh`
   - Check directory permissions for writing reports: `chmod -R 755 reports/`

### Logging

- Application logs are stored in `app.log` in the project root directory
- For more detailed logs, run the application with the `--verbose` flag
- To redirect logs to a specific file: `./main.py "Topic" > custom_log.txt 2>&1`

## Performance Optimization

- For larger research tasks, consider increasing your API rate limits
- When using Ollama, ensure your machine has adequate CPU/RAM resources
- For production use with Ollama, a GPU is recommended for better performance 