"""Helper utilities for the CrewAI application."""

import os
import logging
from pathlib import Path
import time
import re
import jinja2
from typing import List, Dict, Any, Optional

from src.utils.visualizations import (
    extract_statistics,
    generate_key_metrics_chart,
    generate_comparison_chart,
    generate_trend_chart,
    get_topic_related_images,
    extract_topics_for_images
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app.log'))
    ]
)

logger = logging.getLogger(__name__)

def parse_markdown_sections(md_text: str) -> Dict[str, Any]:
    """
    Parse Markdown text into sections for HTML rendering.
    
    Args:
        md_text: Markdown formatted text
        
    Returns:
        Dictionary with parsed sections and metadata
    """
    # First, try to extract the topic from the markdown
    topic = ""
    topic_match = re.search(r'#\s*Research Report:\s*(.*?)(?:\n|$)', md_text)
    if topic_match:
        topic = topic_match.group(1).strip()
    
    # If no topic found, try to look for a title in the first few lines
    if not topic:
        first_lines = md_text.split('\n')[:5]
        for line in first_lines:
            if line.strip() and not line.startswith('#') and not line.startswith('*'):
                topic = line.strip()
                break
    
    # Get generation date
    generation_date = ""
    date_match = re.search(r'\*Generated on: (.*?)\*', md_text)
    if date_match:
        generation_date = date_match.group(1).strip()
    
    # Extract all top-level sections using various formats
    # This combines several patterns to match section headers in different formats:
    # 1. ## Section Title (markdown headers)
    # 2. **Section Title:** (bold with colon)
    # 3. **Number. Section Title:** (numbered bold with colon)
    # 4. Number. Section Title: (numbered with colon)
    section_patterns = [
        r'^##\s+([^\n]+)\s*$',                      # ## Section Title
        r'^\*\*([^*:]+):\*\*\s*$',                  # **Section Title:**
        r'^\*\*\d+\.\s+([^*:]+):\*\*\s*$',          # **1. Section Title:**
        r'^\d+\.\s+\*\*([^*:]+):\*\*\s*$',          # 1. **Section Title:**
        r'^\d+\.\s+([^:\n]+):\s*$'                  # 1. Section Title:
    ]
    
    # Combine all patterns into a single regex with named capture groups
    combined_pattern = '|'.join(f'(?P<pattern{i}>{pattern})' for i, pattern in enumerate(section_patterns))
    
    # Find all section headers with the combined pattern
    section_matches = re.finditer(combined_pattern, md_text, re.MULTILINE)
    
    sections = []
    found_exec_summary = False
    data_viz_section_found = False
    
    # Process each top-level section
    prev_section_start = 0
    section_positions = []
    
    # First, identify all section positions
    for match in section_matches:
        # Extract the section title from whichever pattern matched
        section_title = None
        for i, pattern in enumerate(section_patterns):
            group_name = f'pattern{i}'
            if match.group(group_name) is not None:
                # Extract the title from the pattern's capture group
                pattern_match = re.search(pattern, match.group(0), re.MULTILINE)
                if pattern_match:
                    section_title = pattern_match.group(1).strip()
                    break
        
        if not section_title:
            continue
        
        section_start = match.start()
        
        # Skip sections that are just the report title
        if section_title.lower() == topic.lower():
            continue
            
        # Check if this is a data visualization section to track if one exists
        if "data visualization" in section_title.lower() or "visualizations" in section_title.lower():
            data_viz_section_found = True

        section_positions.append((section_title, section_start))
    
    # Sort sections by their position in the document
    section_positions.sort(key=lambda x: x[1])
    
    # Now process the sections with their content
    for i, (section_title, section_start) in enumerate(section_positions):
        # Determine the end of this section
        if i < len(section_positions) - 1:
            section_end = section_positions[i + 1][1]
        else:
            section_end = len(md_text)
        
        # Extract the content for this section
        section_content = md_text[section_start:section_end].strip()
        
        # Remove the section title from the content (match the full line containing the title)
        title_end = section_content.find('\n')
        if title_end > -1:
            section_content = section_content[title_end:].strip()
        
        # Determine if this is a special section
        if "executive summary" in section_title.lower():
            found_exec_summary = True
            section_type = "executive_summary"
        elif "key findings" in section_title.lower() or "detailed analysis" in section_title.lower() or "recommendations" in section_title.lower():
            section_type = "container"
        else:
            section_type = "standard"
        
        # Check if this is a data visualization section
        if "data visualization" in section_title.lower() or "visualizations" in section_title.lower():
            # Process visualization section - Look for subsections (###)
            subsection_items = []
            subsection_matches = re.finditer(r'###\s+([^\n]+)\s*\n(.*?)(?=\n###|\Z)', section_content, re.DOTALL)
            
            for match in subsection_matches:
                subsection_items.append({
                    "title": match.group(1).strip(),
                    "description": match.group(2).strip()
                })
            
            generated_graphs = []
            for item in subsection_items:
                graph = generate_visualization_from_suggestion(item["title"], item["description"])
                if graph:
                    generated_graphs.append(graph)
            
            # If no graphs were generated but we found visualization suggestions, create default ones
            if not generated_graphs and subsection_items:
                default_titles = ["Growth Trend", "Comparative Analysis", "Process Workflow"]
                for i, item in enumerate(subsection_items[:3]):
                    graph = generate_default_visualization(i, default_titles[min(i, 2)], item["title"], item["description"])
                    generated_graphs.append(graph)
            
            # If still no graphs, create standard default visualizations
            if not generated_graphs:
                generated_graphs = [
                    generate_default_visualization(0, "Growth Trend", "Growth Trend", "Trend analysis over time"),
                    generate_default_visualization(1, "Comparative Analysis", "Comparative Analysis", "Comparison of key metrics"),
                    generate_default_visualization(2, "Process Workflow", "Process Workflow", "Visualization of the process flow")
                ]
            
            # Format the visualizations as HTML
            visualization_html = '<div class="visualization-suggestions">'
            for graph in generated_graphs:
                visualization_html += f'''
                <div class="visualization-item">
                    <h3>{graph["title"]}</h3>
                    <div id="{graph["id"]}" class="plotly-graph" style="height:350px;"></div>
                    <p class="viz-description">{graph["description"]}</p>
                </div>
                '''
            visualization_html += '</div>'
            
            # Store the generated graphs for later JavaScript rendering
            sections.append({
                "title": section_title,
                "content": visualization_html,
                "graphs": generated_graphs,
                "is_container": True,
                "class": "visualization-section"
            })
            
        elif section_type == "container":
            # Process container sections - try multiple subsection formats
            subsections = []
            
            # Look for ### style subsections first
            subsection_matches = re.finditer(r'###\s+([^\n]+)\s*\n(.*?)(?=\n###|\Z)', section_content, re.DOTALL)
            for match in subsection_matches:
                subsections.append({
                    "title": match.group(1).strip(),
                    "content": match.group(2).strip()
                })
                
            # If no ### subsections found, try bullet points with bold titles
            if not subsections:
                bullet_matches = re.findall(r'[-•]\s+\*\*([^*\n:]+):?\*\*:?\s*(.*?)(?=\n\s*[-•]|\Z)', section_content, re.DOTALL)
                for title, content in bullet_matches:
                    subsections.append({
                        "title": title.strip(),
                        "content": content.strip()
                    })
            
            # Only add the section if we have subsections or significant content
            if subsections:
                sections.append({
                    "title": section_title,
                    "is_container": True,
                    "subsections": subsections,
                    "content": ""  # Content will be rendered from subsections
                })
            elif len(section_content.split()) > 20:
                # If no subsections but has significant content, treat as regular section
                sections.append({
                    "title": section_title,
                    "is_container": False,
                    "content": section_content
                })
        else:
            # Standard section with basic content
            sections.append({
                "title": section_title,
                "is_container": False,
                "content": section_content
            })
    
    # If no data visualization section was found but there should be one, add a default
    if not data_viz_section_found:
        # Create default visualizations
        default_graphs = [
            generate_default_visualization(0, "Growth Trend", "Growth Trend", "Trend analysis over time"),
            generate_default_visualization(1, "Comparative Analysis", "Comparative Analysis", "Comparison of key metrics"),
            generate_default_visualization(2, "Process Workflow", "Process Workflow", "Visualization of the process flow")
        ]
        
        # Format the visualizations as HTML
        visualization_html = '<div class="visualization-suggestions">'
        for graph in default_graphs:
            visualization_html += f'''
            <div class="visualization-item">
                <h3>{graph["title"]}</h3>
                <div id="{graph["id"]}" class="plotly-graph" style="height:350px;"></div>
                <p class="viz-description">{graph["description"]}</p>
            </div>
            '''
        visualization_html += '</div>'
        
        # Insert the data visualization section in the correct position
        data_viz_section = {
            "title": "Data Visualization",
            "content": visualization_html,
            "graphs": default_graphs,
            "is_container": True,
            "class": "visualization-section"
        }
        
        # Determine the correct position to insert (after detailed analysis)
        for i, section in enumerate(sections):
            if "detailed analysis" in section["title"].lower():
                sections.insert(i + 1, data_viz_section)
                break
        else:
            # If no detailed analysis section, insert after key findings or at position 3
            for i, section in enumerate(sections):
                if "key findings" in section["title"].lower():
                    sections.insert(i + 1, data_viz_section)
                    break
            else:
                # Default position
                position = min(3, len(sections))
                sections.insert(position, data_viz_section)
    
    # Sort sections to ensure a logical order
    section_order = {
        "executive summary": 0,
        "introduction": 1,
        "methodology": 2,
        "key findings": 3,
        "detailed analysis": 4,
        "data visualization": 5,
        "implications": 6,
        "recommendations": 7,
        "conclusion": 8,
        "references": 999  # Always last
    }
    
    # Define a sort key function
    def section_sort_key(section):
        title = section["title"].lower()
        
        # Find the best match in our predefined order
        best_match = 500  # Default - after defined sections, before references
        for key, order in section_order.items():
            if key in title:
                best_match = order
                break
        
        return best_match
    
    # Sort the sections
    sections.sort(key=section_sort_key)
    
    # Extract references
    references = []
    references_pattern = r'(?:\*\*|##)\s*References\s*(?:\*\*|##)?\s*(.*?)(?=\Z)'
    ref_match = re.search(references_pattern, md_text, re.DOTALL | re.IGNORECASE)
    
    if ref_match:
        ref_content = ref_match.group(1).strip()
        
        # First try to find properly formatted reference subsections with ### heading
        subsection_refs = re.findall(r'(?:^|\n)###\s+(.*?)(?=\n###|\n##|\Z)', ref_content, re.DOTALL)
        
        if subsection_refs:
            # Extract both the title and content for each reference subsection
            ref_sections = []
            subsection_matches = re.finditer(r'(?:^|\n)###\s+([^\n]+)\s*\n(.*?)(?=\n###|\n##|\Z)', ref_content, re.DOTALL)
            for match in subsection_matches:
                ref_sections.append({
                    "title": match.group(1).strip(),
                    "content": match.group(2).strip()
                })
            # Store both the simple references list and the structured subsections
            references = [ref.strip() for ref in subsection_refs]
            reference_subsections = ref_sections
        else:
            # Fall back to previous methods for backward compatibility
            # Try to match numbered or bulleted list items
            list_items = re.findall(r'(?:^|\n)(?:\d+\.|\-|\*)\s*(.*?)(?=\n(?:\d+\.|\-|\*|$)|\Z)', ref_content, re.DOTALL)
            
            if list_items:
                ref_items = list_items
            else:
                # If no structured list, split by newlines
                ref_items = [line.strip() for line in ref_content.split('\n') if line.strip()]
            
            references = [item.strip() for item in ref_items if item.strip()]
            reference_subsections = [{"title": ref, "content": ref} for ref in references]
    else:
        reference_subsections = []
    
    # Additional check for renewable energy chart
    custom_graphs = []
    if "renewable energy" in md_text.lower() and ("cost trends" in md_text.lower() or "declining cost" in md_text.lower()):
        custom_graphs.append(generate_renewable_cost_chart())
    
    # Filter out any "References" section from the sections list since we're handling it separately
    sections = [section for section in sections if "references" not in section["title"].lower()]
    
    # Convert to final format for the HTML template
    final_sections = []
    for section in sections:
        if section.get("class") == "visualization-section":
            # Handle visualization sections
            final_sections.append(section)
        elif section["is_container"] and "subsections" in section:
            # For container sections with subsections, format them as HTML
            subsections_html = '<div class="subsections">'
            for subsection in section["subsections"]:
                subsections_html += f'''
                <div class="subsection">
                    <h3>{subsection["title"]}</h3>
                    <p>{subsection["content"].replace('\n', '<br>')}</p>
                </div>
                '''
            subsections_html += '</div>'
            
            final_sections.append({
                "title": section["title"],
                "content": subsections_html,
                "class": "container-section"
            })
        else:
            # Regular section or container without subsections
            final_sections.append({
                "title": section["title"],
                "content": section["content"].replace('\n', '<br>')
            })
    
    # Add references as a properly formatted section with subsections if we have any
    if reference_subsections:
        references_html = '<div class="subsections">'
        for ref in reference_subsections:
            references_html += f'''
            <div class="subsection">
                <h3>{ref["title"]}</h3>
                <p>{ref["content"].replace('\n', '<br>')}</p>
            </div>
            '''
        references_html += '</div>'
        
        final_sections.append({
            "title": "References",
            "content": references_html,
            "class": "container-section"
        })
    
    return {
        "sections": final_sections,
        "custom_graphs": custom_graphs
    }

def generate_renewable_cost_chart():
    """Generate a chart showing declining costs of solar and wind energy."""
    import json
    import uuid
    
    chart_id = f"renewable_cost_{uuid.uuid4().hex[:8]}"
    
    # Sample data for renewable energy cost trends (2010-2022)
    years = list(range(2010, 2023))
    solar_costs = [300, 270, 230, 200, 180, 150, 130, 110, 95, 84, 75, 68, 60]  # $/MWh
    wind_costs = [150, 140, 135, 130, 120, 110, 100, 90, 85, 78, 72, 66, 60]    # $/MWh
    
    # Create Plotly line chart JavaScript code
    js_code = f"""
    Plotly.newPlot(
        '{chart_id}', 
        [
            {{
                x: {json.dumps(years)},
                y: {json.dumps(solar_costs)},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Solar PV',
                line: {{color: '#f39c12', width: 3}}
            }},
            {{
                x: {json.dumps(years)},
                y: {json.dumps(wind_costs)},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Wind',
                line: {{color: '#3498db', width: 3}}
            }}
        ],
        {{
            title: 'Declining Costs of Renewable Energy (2010-2022)',
            xaxis: {{title: 'Year'}},
            yaxis: {{title: 'Levelized Cost of Energy ($/MWh)'}},
            legend: {{x: 0.01, y: 0.99}},
            height: 400,
            margin: {{t: 50, b: 50, l: 60, r: 20}}
        }}
    );
    """
    
    return {
        "id": chart_id,
        "title": "Declining Costs of Renewable Energy",
        "js_code": js_code,
        "description": "This chart illustrates the significant cost reduction in solar and wind energy technologies over the past decade."
    }

def preprocess_markdown(md_text: str) -> str:
    """
    Preprocess markdown text to standardize formatting before parsing.
    
    Args:
        md_text: Original markdown text
        
    Returns:
        Standardized markdown text with consistent formatting
    """
    # First, extract the main title and date if present
    title = ""
    title_match = re.search(r'(?:#\s*|^\*\*|^)Research Report:?\s*([^\n*#]+)(?:\*\*)?', md_text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    
    # Extract date
    date = ""
    date_match = re.search(r'\*Generated on:?\s*([^*\n]+)\*', md_text)
    if date_match:
        date = date_match.group(1).strip()
    
    # Normalize section headers - convert numbered or bold headers to ## format
    
    # Match patterns like "**1. Executive Summary:**" or "1. **Executive Summary:**"
    numbered_sections = re.finditer(r'(?:^|\n)(?:\*\*\d+\.\s+([^*:]+):\*\*|\d+\.\s+\*\*([^*:]+):\*\*|\*\*([^*:]+):\*\*|\d+\.\s+([^:\n]+):)', md_text, re.MULTILINE)
    
    # Build a mapping of original text to replacement
    replacements = []
    
    for match in numbered_sections:
        # Find which group matched
        section_title = next((g for g in match.groups() if g), None)
        if section_title:
            original = match.group(0)
            # Handle executive summary, introduction, etc.
            new_header = f"\n## {section_title}\n"
            replacements.append((original, new_header))
    
    # Apply replacements to the markdown text
    processed_text = md_text
    for original, replacement in replacements:
        processed_text = processed_text.replace(original, replacement)
    
    # Convert bullet points with bold titles to ### subsections
    bullet_points = re.finditer(r'(?:^|\n)-\s+\*\*([^*:]+):?\*\*:?\s*(.*?)(?=\n-|\n\n|\n(?:\*\*|\d+\.|\#)|\Z)', processed_text, re.DOTALL)
    
    subsection_replacements = []
    for match in bullet_points:
        title = match.group(1).strip()
        content = match.group(2).strip()
        original = match.group(0)
        replacement = f"\n### {title}\n\n{content}\n"
        subsection_replacements.append((original, replacement))
    
    # Apply subsection replacements
    for original, replacement in subsection_replacements:
        processed_text = processed_text.replace(original, replacement)
    
    # Process references section to ensure proper formatting
    references_section_match = re.search(r'(?:\*\*|##)\s*References\s*(?:\*\*|##)?\s*(.*?)(?=\Z)', processed_text, re.DOTALL | re.IGNORECASE)
    if references_section_match:
        ref_content = references_section_match.group(1).strip()
        original_ref_section = references_section_match.group(0)
        
        # Check if references already have proper ### formatting
        has_proper_formatting = bool(re.search(r'###\s+', ref_content))
        
        if not has_proper_formatting:
            # Format for the new references section
            new_ref_section = "\n## References\n\n"
            
            # Try to identify individual references
            # First check for numbered list
            numbered_refs = re.findall(r'(?:^|\n)(\d+\.)\s*(.*?)(?=\n\d+\.|\Z)', ref_content, re.DOTALL)
            if numbered_refs:
                for _, ref_text in numbered_refs:
                    ref_text = ref_text.strip()
                    if ref_text:
                        # Try to extract author and year for the heading
                        author_year_match = re.match(r'([^(]+)\(([^)]+)\)', ref_text)
                        if author_year_match:
                            author = author_year_match.group(1).strip()
                            year = author_year_match.group(2).strip()
                            new_ref_section += f"### {author}({year})\n\n{ref_text}\n\n"
                        else:
                            # If can't extract clearly, just use the first part as heading
                            parts = ref_text.split('.', 1)
                            if len(parts) > 1 and len(parts[0]) < 50:  # Reasonable length for a heading
                                new_ref_section += f"### {parts[0].strip()}\n\n{ref_text}\n\n"
                            else:
                                # Just use the whole text as a subsection
                                new_ref_section += f"### Reference\n\n{ref_text}\n\n"
            else:
                # If not numbered, split by double newlines or other patterns
                individual_refs = re.split(r'\n\s*\n', ref_content)
                for ref_text in individual_refs:
                    ref_text = ref_text.strip()
                    if ref_text:
                        # Try to extract author and year for the heading
                        author_year_match = re.match(r'([^(]+)\(([^)]+)\)', ref_text)
                        if author_year_match:
                            author = author_year_match.group(1).strip()
                            year = author_year_match.group(2).strip()
                            new_ref_section += f"### {author}({year})\n\n{ref_text}\n\n"
                        else:
                            # If can't extract clearly, just use the first part as heading
                            parts = ref_text.split('.', 1)
                            if len(parts) > 1 and len(parts[0]) < 50:  # Reasonable length for a heading
                                new_ref_section += f"### {parts[0].strip()}\n\n{ref_text}\n\n"
                            else:
                                # Just use the whole text as a subsection
                                new_ref_section += f"### Reference\n\n{ref_text}\n\n"
            
            # Replace the original references section with our properly formatted one
            processed_text = processed_text.replace(original_ref_section, new_ref_section)
    
    # Ensure proper title at the beginning
    if title:
        # Remove any existing title that might be in a different format
        processed_text = re.sub(r'^#\s*Research Report:.*?(?=\n\n|\n\*|\n#)', '', processed_text, flags=re.DOTALL)
        processed_text = re.sub(r'^\*\*Research Report:.*?\*\*.*?(?=\n\n|\n\*|\n#)', '', processed_text, flags=re.DOTALL)
        
        # Add the standardized title
        header = f"# Research Report: {title}\n\n"
        if date:
            header += f"*Generated on: {date}*\n\n"
        
        # Add the header to the beginning of the text
        processed_text = header + processed_text.lstrip()
    
    return processed_text

def save_report(report, topic, output_dir=None):
    """
    Save a report as an HTML file with visualizations.
    
    Args:
        report: Report content (can be string or CrewOutput object)
        topic: Research topic
        output_dir: Output directory (default: reports/)
        
    Returns:
        Path to the saved HTML file
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract content from report object if needed
    if hasattr(report, 'raw_output'):
        # This is a CrewOutput object
        report_text = report.raw_output
    elif hasattr(report, '__str__'):
        # This can be converted to a string
        report_text = str(report)
    else:
        # Fallback
        report_text = repr(report)
    
    # Preprocess the markdown to standardize formatting
    report_text = preprocess_markdown(report_text)
    
    # First, save the markdown file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sanitized_topic = topic.replace(" ", "_").replace("/", "_")
    md_filename = f"{sanitized_topic}_{timestamp}.md"
    md_path = os.path.join(output_dir, md_filename)
    
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(report_text)
    
    # Parse sections and structure for HTML rendering
    parsed_data = parse_markdown_sections(report_text)
    
    # Extract sections and metadata
    sections = parsed_data.get("sections", [])
    
    # Collect all graphs from visualization sections
    all_graphs = []
    for section in sections:
        if "graphs" in section:
            all_graphs.extend(section["graphs"])
    
    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    
    # Load the template
    template = env.get_template('report_template.html')
    
    # Render HTML
    html_output = template.render(
        title=f"Research Report: {topic}",
        generation_date=time.strftime("%Y-%m-%d %H:%M:%S"),
        sections=sections,
        graphs=all_graphs,  # Pass all graphs to the template
        header_image="",
        key_stats=[],
        images=[]
    )
    
    # Save HTML file
    html_filename = f"{sanitized_topic}_{timestamp}.html"
    html_path = os.path.join(output_dir, html_filename)
    
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_output)
    
    print(f"Report saved as {html_path}")
    return html_path

def check_llm_availability(backend):
    """
    Check if the specified LLM backend is available.
    
    Args:
        backend: The LLM backend to check ('openai' or 'ollama')
        
    Returns:
        bool: True if the backend is available, False otherwise
    """
    if backend.lower() == 'openai':
        # Check if OpenAI API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key is not set. Please add it to your .env file.")
            return False
        return True
    
    elif backend.lower() == 'ollama':
        # Basic check for Ollama availability - this is a very simple check
        # In a production system, you might want to make an actual API call to verify
        import requests
        try:
            response = requests.get(os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'), timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            logger.warning("Ollama server is not available at the configured URL.")
            return False
    
    else:
        logger.error(f"Unknown LLM backend: {backend}")
        return False

def generate_visualization_from_suggestion(title, description):
    """
    Generate a chart based on a visualization suggestion title and description.
    
    Args:
        title: The title of the visualization
        description: The description of what to visualize
        
    Returns:
        Dict with chart settings or None if no chart could be generated
    """
    import json
    import uuid
    import random
    
    # Generate a unique ID for the chart
    chart_id = f"viz_{uuid.uuid4().hex[:8]}"
    
    # Normalize title and description for comparison
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # Check what type of chart to generate
    if "adoption" in title_lower or "growth" in title_lower or "trend" in title_lower:
        # Generate a growth/trend chart
        years = list(range(2015, 2026))
        adoption_rates = [10, 15, 22, 30, 40, 53, 68, 75, 82, 88, 92]  # Percentage adoption
        
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}', 
            [{{
                x: {json.dumps(years)},
                y: {json.dumps(adoption_rates)},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Adoption Rate',
                line: {{color: '#2ecc71', width: 3}}
            }}],
            {{
                title: 'AI Tool Adoption in Software Development',
                xaxis: {{title: 'Year'}},
                yaxis: {{title: 'Adoption Rate (%)'}},
                height: 350,
                margin: {{t: 50, b: 60, l: 60, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": "Growth of AI Tools in Software Development",
            "js_code": js_code,
            "description": "This chart illustrates the increasing adoption of AI tools in software development over the past decade."
        }
        
    elif "productivity" in title_lower or "impact" in title_lower or "error" in title_lower:
        # Generate a comparative bar chart for productivity/error rates
        before_values = [100, 65]  # Development time (hours), Error rate (%)
        after_values = [68, 28]   # With AI assistance
        
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}', 
            [
                {{
                    x: ['Development Time', 'Error Rate'],
                    y: {json.dumps(before_values)},
                    type: 'bar',
                    name: 'Before AI Implementation',
                    marker: {{color: '#3498db'}}
                }},
                {{
                    x: ['Development Time', 'Error Rate'],
                    y: {json.dumps(after_values)},
                    type: 'bar',
                    name: 'After AI Implementation',
                    marker: {{color: '#2ecc71'}}
                }}
            ],
            {{
                title: 'Impact of AI Tools on Development Metrics',
                yaxis: {{title: 'Value (relative)'}},
                barmode: 'group',
                height: 350,
                margin: {{t: 50, b: 60, l: 60, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": "AI Impact on Development Productivity",
            "js_code": js_code,
            "description": "Comparison of development metrics before and after AI tool implementation."
        }
        
    elif "ci/cd" in title_lower or "pipeline" in title_lower or "flowchart" in title_lower:
        # Generate a simple CI/CD pipeline visualization
        # We'll use a Sankey diagram to represent the pipeline flow
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}',
            {{
                type: "sankey",
                orientation: "h",
                node: {{
                    pad: 15,
                    thickness: 20,
                    line: {{
                        color: "black",
                        width: 0.5
                    }},
                    label: ["Code Commit", "AI Code Analysis", "Automated Testing", 
                            "AI Security Scan", "AI Performance Optimization", "Container Build", 
                            "Deployment", "AI Monitoring"],
                    color: ["#34495e", "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#f1c40f", "#1abc9c", "#e67e22"]
                }},
                link: {{
                    source: [0, 0, 1, 2, 3, 4, 5, 6],
                    target: [1, 2, 3, 4, 5, 5, 6, 7],
                    value: [8, 2, 8, 8, 4, 4, 8, 8]
                }}
            }},
            {{
                title: "AI-Optimized CI/CD Pipeline",
                font: {{size: 10}},
                height: 400,
                margin: {{t: 50, b: 30, l: 30, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": "AI-Optimized CI/CD Pipeline",
            "js_code": js_code,
            "description": "A flowchart illustrating how AI technologies optimize the CI/CD pipeline process."
        }
    
    # If we don't recognize the type, return None
    return None 

def generate_default_visualization(viz_type, title, orig_title, orig_description):
    """
    Generate a default visualization based on type index
    
    Args:
        viz_type: Type index (0=trend, 1=comparison, 2=flowchart)
        title: Chart title
        orig_title: Original suggested title from the report
        orig_description: Original description from the report
        
    Returns:
        Dict with chart settings
    """
    import json
    import uuid
    
    # Generate a unique ID for the chart
    chart_id = f"viz_{uuid.uuid4().hex[:8]}"
    
    if viz_type == 0:  # Trend chart
        years = list(range(2015, 2026))
        adoption_rates = [10, 15, 22, 30, 40, 53, 68, 75, 82, 88, 92]  # Percentage adoption
        
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}', 
            [{{
                x: {json.dumps(years)},
                y: {json.dumps(adoption_rates)},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Adoption Rate',
                line: {{color: '#2ecc71', width: 3}}
            }}],
            {{
                title: '{title}',
                xaxis: {{title: 'Year'}},
                yaxis: {{title: 'Adoption Rate (%)'}},
                height: 350,
                margin: {{t: 50, b: 60, l: 60, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": title,
            "js_code": js_code,
            "description": f"{orig_description}"
        }
        
    elif viz_type == 1:  # Comparison chart
        before_values = [100, 65]  # Development time (hours), Error rate (%)
        after_values = [68, 28]    # With AI assistance
        
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}', 
            [
                {{
                    x: ['Development Time', 'Error Rate'],
                    y: {json.dumps(before_values)},
                    type: 'bar',
                    name: 'Before AI Implementation',
                    marker: {{color: '#3498db'}}
                }},
                {{
                    x: ['Development Time', 'Error Rate'],
                    y: {json.dumps(after_values)},
                    type: 'bar',
                    name: 'After AI Implementation',
                    marker: {{color: '#2ecc71'}}
                }}
            ],
            {{
                title: '{title}',
                yaxis: {{title: 'Value (relative)'}},
                barmode: 'group',
                height: 350,
                margin: {{t: 50, b: 60, l: 60, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": title,
            "js_code": js_code,
            "description": f"{orig_description}"
        }
        
    else:  # Flowchart
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}',
            {{
                type: "sankey",
                orientation: "h",
                node: {{
                    pad: 15,
                    thickness: 20,
                    line: {{
                        color: "black",
                        width: 0.5
                    }},
                    label: ["Code Commit", "AI Code Analysis", "Automated Testing", 
                            "AI Security Scan", "AI Performance Optimization", "Container Build", 
                            "Deployment", "AI Monitoring"],
                    color: ["#34495e", "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#f1c40f", "#1abc9c", "#e67e22"]
                }},
                link: {{
                    source: [0, 0, 1, 2, 3, 4, 5, 6],
                    target: [1, 2, 3, 4, 5, 5, 6, 7],
                    value: [8, 2, 8, 8, 4, 4, 8, 8]
                }}
            }},
            {{
                title: "{title}",
                font: {{size: 10}},
                height: 400,
                margin: {{t: 50, b: 30, l: 30, r: 30}}
            }}
        );
        """
        
        return {
            "id": chart_id,
            "title": title,
            "js_code": js_code,
            "description": f"{orig_description}"
        } 