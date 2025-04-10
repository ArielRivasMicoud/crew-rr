#!/bin/bash
# Setup script for the CrewAI Research and Reporting application

set -e  # Exit on error

echo "Setting up CrewAI Research and Reporting application..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up environment variables if not already done
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit the .env file to add your API keys and configuration."
else
    echo ".env file already exists."
fi

# Create necessary directories
echo "Creating report directories..."
mkdir -p reports/openai reports/ollama

# Make scripts executable
echo "Making scripts executable..."
chmod +x main.py example.py

echo "Setup complete!"
echo "To run the application, execute:"
echo "  source venv/bin/activate"
echo "  ./main.py \"Your research topic\""
echo ""
echo "Don't forget to edit your .env file to add your API keys!" 