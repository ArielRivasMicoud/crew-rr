# CrewAI Research and Reporting Application

A multi-agent application built with CrewAI that uses two specialized agents (a Senior Data Researcher and a Reporting Analyst) to collaboratively research a topic and generate a comprehensive report.

## Features

- Two specialized agents with distinct roles and expertise
- Configurable LLM backends (OpenAI API and local Ollama models)
- Structured research and reporting workflow
- Rich HTML reports with data visualizations and relevant images
- Output saved as both HTML and Markdown files
- Modular and extensible architecture

## Project Structure

```
/
├── main.py                     # Main entry point
├── requirements.txt            # Dependencies
├── .env.example                # Example environment variables
├── src/                        # Source code
│   ├── agents/                 # Agent definitions
│   ├── config/                 # Configuration
│   ├── crew/                   # Crew definitions
│   ├── tasks/                  # Task definitions
│   ├── tools/                  # Custom tools for agents
│   └── utils/                  # Utility functions
└── reports/                    # Generated reports (created on first run)
```

## Installation

1. Clone the repository (or create the file structure as shown above)

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file to add your OpenAI API key and configure other settings.

## LLM Backend Configuration

### OpenAI

1. Sign up for an OpenAI API key at https://platform.openai.com/
2. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o  # or another model of your choice
   ```

### Ollama (Local LLM)

1. Install Ollama from https://ollama.ai/
2. Pull a model (e.g., llama3):
   ```bash
   ollama pull llama3
   ```
3. Configure Ollama in the `.env` file:
   ```
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3  # or another model you've pulled
   ```
4. To use Ollama as the default backend, set:
   ```
   DEFAULT_LLM_BACKEND=ollama
   ```

## Image API Configuration (Optional)

For enhanced reports with relevant images, you can provide API keys for:

1. **Unsplash API**:
   - Register at https://unsplash.com/developers
   - Add your access key to the `.env` file:
     ```
     UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
     ```

2. **Pexels API**:
   - Register at https://www.pexels.com/api/
   - Add your API key to the `.env` file:
     ```
     PEXELS_API_KEY=your_pexels_access_key_here
     ```

If no API keys are provided, the application will use placeholder images.

## Usage

Run the application with a research topic:

```bash
python main.py "Climate change impacts on agriculture"
```

Use a specific LLM backend:

```bash
python main.py "Renewable energy trends" --backend openai
python main.py "Artificial intelligence ethics" --backend ollama
```

Specify an output directory for the report:

```bash
python main.py "Space exploration" --output-dir ./my_reports
```

Enable verbose output:

```bash
python main.py "Quantum computing applications" --verbose
```

## Example Output

The application generates a comprehensive report saved as both HTML and Markdown files in the `reports/` directory. The reports include:

### HTML Report with Visualizations
- Interactive data visualizations based on statistics in the report
- Relevant images related to the topic
- Well-formatted sections with proper styling
- Mobile-responsive design for easy reading on any device

### Content Sections
- Executive Summary
- Introduction
- Methodology
- Key Findings and Insights
- Detailed Analysis
- Data Visualization Suggestions
- Implications
- Recommendations
- Conclusion
- References

## Extending the Application

### Adding New Agents

1. Create a new agent definition in `src/agents/`
2. Update the crew in `src/crew/research_crew.py` to include the new agent

### Creating Custom Tools

1. Add new tool definitions in `src/tools/`
2. Import and use the tools in your agent tasks

### Supporting Additional LLM Backends

1. Update `src/config/llm_config.py` to add support for the new backend
2. Modify `src/config/settings.py` to include configuration for the new backend

### Customizing Report Templates

1. Modify the HTML template in `src/utils/templates/report_template.html`
2. Add new visualization types in `src/utils/visualizations.py`

## Troubleshooting

- **OpenAI API errors**: Ensure your API key is correct and you have sufficient credits
- **Ollama errors**: Make sure Ollama is running and you've pulled the model you're trying to use
- **Import errors**: Verify that all dependencies are installed correctly
- **Image API errors**: Check your API keys and connection

## License

This project is open source and available under the MIT License. 