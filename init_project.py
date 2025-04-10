#!/usr/bin/env python3
"""
CrewAI Project Initializer

This script creates a new CrewAI project with the basic structure
and files needed to get started quickly.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Initialize a new CrewAI project with basic structure and files.'
    )
    
    parser.add_argument(
        'project_name',
        type=str,
        help='Name of the new project (will be created as a directory)'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default=os.getcwd(),
        help='Path where the project should be created (default: current directory)'
    )
    
    parser.add_argument(
        '--template',
        type=str,
        choices=['basic', 'research'],
        default='basic',
        help='Project template to use (default: basic)'
    )
    
    return parser.parse_args()

def create_project_structure(project_path, template):
    """Create the basic project structure."""
    dirs = [
        'src/agents',
        'src/config',
        'src/crew',
        'src/tasks',
        'src/tools',
        'src/utils',
        'tests',
        'reports'
    ]
    
    for dir_path in dirs:
        full_path = os.path.join(project_path, dir_path)
        os.makedirs(full_path, exist_ok=True)
        # Create __init__.py files
        with open(os.path.join(full_path, '__init__.py'), 'w') as f:
            f.write(f'"""Package for {dir_path}."""\n')
    
    logger.info(f"Created project structure in {project_path}")

def copy_template_files(project_path, template):
    """Copy template files to the new project."""
    # Get the current script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # These files should be copied from the current project
    files_to_copy = [
        '.env.example',
        '.gitignore',
        'requirements.txt',
        'setup.sh',
        'README.md'
    ]
    
    for file in files_to_copy:
        source = os.path.join(script_dir, file)
        destination = os.path.join(project_path, file)
        
        if os.path.exists(source):
            shutil.copy2(source, destination)
            logger.info(f"Copied {file} to project")
        else:
            logger.warning(f"Template file {file} not found, skipping")
    
    # Copy main.py with modified content
    with open(os.path.join(script_dir, 'main.py'), 'r') as f:
        content = f.read()
    
    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(content)
    
    # Make scripts executable
    os.chmod(os.path.join(project_path, 'main.py'), 0o755)
    os.chmod(os.path.join(project_path, 'setup.sh'), 0o755)
    
    logger.info("Made scripts executable")

def create_custom_readme(project_path, project_name):
    """Create a custom README.md file for the project."""
    readme_path = os.path.join(project_path, 'README.md')
    
    with open(readme_path, 'w') as f:
        f.write(f"# {project_name}\n\n")
        f.write("A multi-agent application built with CrewAI.\n\n")
        f.write("## Setup\n\n")
        f.write("1. Run the setup script:\n")
        f.write("   ```bash\n")
        f.write("   ./setup.sh\n")
        f.write("   ```\n\n")
        f.write("2. Edit the `.env` file to add your API keys.\n\n")
        f.write("3. Run the application:\n")
        f.write("   ```bash\n")
        f.write("   ./main.py \"Your topic\"\n")
        f.write("   ```\n")
    
    logger.info("Created custom README.md")

def main():
    """Initialize a new CrewAI project."""
    args = parse_args()
    
    # Create the project directory
    project_path = os.path.join(args.path, args.project_name)
    
    # Check if the directory already exists
    if os.path.exists(project_path):
        logger.error(f"Error: Directory {project_path} already exists.")
        return 1
    
    # Create the project directory
    os.makedirs(project_path)
    logger.info(f"Created project directory: {project_path}")
    
    # Create the project structure
    create_project_structure(project_path, args.template)
    
    # Copy template files
    copy_template_files(project_path, args.template)
    
    # Create custom README
    create_custom_readme(project_path, args.project_name)
    
    logger.info(f"\nProject {args.project_name} initialized successfully!")
    logger.info(f"To get started, run:\n")
    logger.info(f"  cd {args.project_name}")
    logger.info(f"  ./setup.sh")
    logger.info(f"  # Edit .env file to add your API keys")
    logger.info(f"  ./main.py \"Your topic\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 