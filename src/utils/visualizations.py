"""Utilities for creating data visualizations and handling images for reports."""

import re
import os
import json
import base64
import uuid
import requests
from io import BytesIO
import logging
import random
from typing import List, Dict, Any, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Constants
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')

def extract_statistics(report_text: str) -> List[Dict[str, Any]]:
    """
    Extract statistics and data points from the report text.
    
    Args:
        report_text: The report text to extract statistics from
        
    Returns:
        List of dictionaries containing statistics
    """
    stats = []
    
    # Look for patterns like "$X billion", "X%" or "X million"
    currency_pattern = r'\$(\d+(?:\.\d+)?)\s*(billion|million|trillion)'
    percentage_pattern = r'(\d+(?:\.\d+)?)%'
    number_pattern = r'(\d+(?:\.\d+)?)\s*(million|billion|trillion)'
    
    # Extract currency values
    currency_matches = re.finditer(currency_pattern, report_text)
    for match in currency_matches:
        value = float(match.group(1))
        unit = match.group(2)
        
        # Context - try to get a few words before the match
        start_pos = max(0, match.start() - 50)
        context = report_text[start_pos:match.start()]
        context_words = context.split()[-5:] if context.split() else []
        
        title = ' '.join(context_words) if context_words else "Market Value"
        
        stats.append({
            "title": title.strip().capitalize(),
            "value": f"${value}",
            "description": f"In {unit}"
        })
    
    # Extract percentages
    percentage_matches = re.finditer(percentage_pattern, report_text)
    for match in percentage_matches:
        value = match.group(1)
        
        # Context
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(report_text), match.start() + 50)
        context = report_text[start_pos:end_pos]
        
        # Try to extract a meaningful title
        title_match = re.search(r'([A-Z][a-z]+(?:\s+[a-z]+){1,4})', context)
        title = title_match.group(1) if title_match else "Growth Rate"
        
        stats.append({
            "title": title.strip().capitalize(),
            "value": f"{value}%",
            "description": "Annual Rate" if "annual" in context.lower() or "year" in context.lower() else "Growth Rate"
        })
    
    # Return a maximum of 4 stats to avoid cluttering the report
    return stats[:4]

def generate_key_metrics_chart(stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a bar chart for key metrics from the statistics.
    
    Args:
        stats: List of statistics dictionaries
        
    Returns:
        Dictionary with chart configuration
    """
    if not stats:
        return None
    
    # Extract numeric values from the stats
    chart_data = []
    for stat in stats:
        # Extract numeric value from the stat value
        value_str = stat["value"]
        numeric_value = float(re.sub(r'[^\d.]', '', value_str))
        
        # Handle percentage values
        if "%" in value_str:
            value_type = "percentage"
        elif "$" in value_str:
            value_type = "currency"
        else:
            value_type = "number"
        
        chart_data.append({
            "title": stat["title"],
            "value": numeric_value,
            "type": value_type
        })
    
    # Create chart ID
    chart_id = f"key_metrics_{uuid.uuid4().hex[:8]}"
    
    # Create Plotly figure
    titles = [item["title"] for item in chart_data]
    values = [item["value"] for item in chart_data]
    
    # Create a horizontal bar chart with custom colors
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12'][:len(chart_data)]
    
    # Generate JavaScript code for the chart
    js_code = f"""
    Plotly.newPlot(
        '{chart_id}', 
        [{{"x": {json.dumps(values)}, 
           "y": {json.dumps(titles)}, 
           "type": 'bar',
           "orientation": 'h',
           "marker": {{"color": {json.dumps(colors)}}}
         }}],
        {{"margin": {{"t": 10, "b": 40, "l": 140, "r": 10}},
          "height": 300,
          "yaxis": {{"automargin": true}},
          "xaxis": {{"title": "Value"}}
        }}
    );
    """
    
    return {
        "id": chart_id,
        "title": "Key Metrics",
        "js_code": js_code,
        "description": "Visual representation of key metrics extracted from the report."
    }

def generate_comparison_chart(report_text: str) -> Optional[Dict[str, Any]]:
    """
    Generate a comparison chart based on entities mentioned in the report.
    
    Args:
        report_text: The report text to extract comparisons from
        
    Returns:
        Dictionary with chart configuration or None if no comparisons found
    """
    # Look for patterns suggesting comparisons between entities
    # This is a simplified approach - a more sophisticated NLP approach would be better
    patterns = [
        r'((?:(?:[A-Z][a-z]+)\s*)+)(?:,|\s+and\s+)((?:(?:[A-Z][a-z]+)\s*)+)(?:,|\s+and\s+)((?:(?:[A-Z][a-z]+)\s*)+).*?(?:top|leading|major)',
        r'((?:(?:[A-Z][a-z]+)\s*)+)(?:,|\s+and\s+)((?:(?:[A-Z][a-z]+)\s*)+)(?:,|\s+and\s+)((?:(?:[A-Z][a-z]+)\s*)+).*?(?:producers?|consumers?|countries|markets)'
    ]
    
    entities = []
    for pattern in patterns:
        matches = re.finditer(pattern, report_text)
        for match in matches:
            entities.extend([g.strip() for g in match.groups() if g and len(g.strip()) > 2])
    
    # If we found entities, create a comparison chart
    if entities:
        # De-duplicate and take up to 5 entities
        entities = list(set([e for e in entities if len(e.split()) < 3]))[:5]
        
        if len(entities) >= 2:
            # Generate random data for the entities (in a real app, you'd use actual data)
            values = [random.randint(20, 100) for _ in entities]
            
            chart_id = f"comparison_{uuid.uuid4().hex[:8]}"
            
            # Create a pie chart
            js_code = f"""
            Plotly.newPlot(
                '{chart_id}', 
                [{{"values": {json.dumps(values)}, 
                   "labels": {json.dumps(entities)}, 
                   "type": 'pie',
                   "textinfo": "label+percent",
                   "insidetextorientation": "radial"
                 }}],
                {{"margin": {{"t": 30, "b": 30, "l": 30, "r": 30}},
                  "height": 400
                }}
            );
            """
            
            # Determine the type of entities
            entity_type = "Producers" if "producer" in report_text.lower() else \
                          "Countries" if "countr" in report_text.lower() else \
                          "Companies" if any(e.endswith("Inc") or e.endswith("Co") for e in entities) else \
                          "Market Share"
            
            return {
                "id": chart_id,
                "title": f"{entity_type} Comparison",
                "js_code": js_code,
                "description": f"Relative comparison of {entity_type.lower()} mentioned in the report. Values are illustrative."
            }
    
    return None

def generate_trend_chart(report_text: str) -> Optional[Dict[str, Any]]:
    """
    Generate a trend chart based on growth trends mentioned in the report.
    
    Args:
        report_text: The report text to extract growth trends from
        
    Returns:
        Dictionary with chart configuration or None if no trends found
    """
    # Look for CAGR or growth trend mentions
    cagr_pattern = r'(?:CAGR|growth rate|annual growth|compound annual growth rate).*?(\d+(?:\.\d+)?)%'
    match = re.search(cagr_pattern, report_text, re.IGNORECASE)
    
    if match:
        growth_rate = float(match.group(1))
        
        # Generate a trend line for the next 5 years
        years = list(range(2023, 2028))
        base_value = 100
        values = [base_value * ((1 + growth_rate/100) ** i) for i in range(5)]
        
        chart_id = f"trend_{uuid.uuid4().hex[:8]}"
        
        # Create a line chart
        js_code = f"""
        Plotly.newPlot(
            '{chart_id}', 
            [{{"x": {json.dumps(years)}, 
               "y": {json.dumps(values)}, 
               "type": 'scatter',
               "mode": 'lines+markers',
               "name": 'Projected Growth',
               "line": {{"color": '#3498db', "width": 3}}
             }}],
            {{"margin": {{"t": 30, "b": 50, "l": 50, "r": 30}},
              "height": 350,
              "xaxis": {{"title": "Year"}},
              "yaxis": {{"title": "Value (indexed to 100)"}}
            }}
        );
        """
        
        # Try to determine what is growing
        context_start = max(0, match.start() - 100)
        context_end = min(len(report_text), match.start())
        context = report_text[context_start:context_end]
        
        subject_match = re.search(r'(market|industry|demand|consumption|production)', context, re.IGNORECASE)
        subject = subject_match.group(1).capitalize() if subject_match else "Market"
        
        return {
            "id": chart_id,
            "title": f"{subject} Growth Projection ({growth_rate}% CAGR)",
            "js_code": js_code,
            "description": f"Projected growth based on the {growth_rate}% CAGR mentioned in the report."
        }
    
    return None

def search_unsplash_images(query: str, count: int = 3) -> List[Dict[str, str]]:
    """
    Search for images on Unsplash related to the topic.
    
    Args:
        query: The search query
        count: Number of images to return
        
    Returns:
        List of dictionaries with image information
    """
    if not UNSPLASH_ACCESS_KEY:
        logger.warning("No Unsplash API key provided. Using placeholder images.")
        return get_placeholder_images(query, count)
    
    try:
        encoded_query = quote_plus(query)
        url = f"https://api.unsplash.com/search/photos?query={encoded_query}&per_page={count}"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "results" in data and data["results"]:
            images = []
            for img in data["results"]:
                images.append({
                    "url": img["urls"]["regular"],
                    "alt": img["alt_description"] or query,
                    "caption": f"Photo by {img['user']['name']} on Unsplash",
                })
            return images
    except Exception as e:
        logger.error(f"Error searching Unsplash: {e}")
    
    return get_placeholder_images(query, count)

def search_pexels_images(query: str, count: int = 3) -> List[Dict[str, str]]:
    """
    Search for images on Pexels related to the topic.
    
    Args:
        query: The search query
        count: Number of images to return
        
    Returns:
        List of dictionaries with image information
    """
    if not PEXELS_API_KEY:
        logger.warning("No Pexels API key provided. Using placeholder images.")
        return get_placeholder_images(query, count)
    
    try:
        encoded_query = quote_plus(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page={count}"
        headers = {"Authorization": PEXELS_API_KEY}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "photos" in data and data["photos"]:
            images = []
            for img in data["photos"]:
                images.append({
                    "url": img["src"]["large"],
                    "alt": f"{query} image",
                    "caption": f"Photo by {img['photographer']} on Pexels",
                })
            return images
    except Exception as e:
        logger.error(f"Error searching Pexels: {e}")
    
    return get_placeholder_images(query, count)

def get_placeholder_images(topic: str, count: int = 3) -> List[Dict[str, str]]:
    """
    Get placeholder images when API access is not available.
    Uses Lorem Picsum for random placeholder images.
    
    Args:
        topic: The topic to use in image captions
        count: Number of images to return
        
    Returns:
        List of dictionaries with image information
    """
    images = []
    base_url = "https://picsum.photos"
    
    for i in range(count):
        # Generate a unique ID for each image
        img_id = (hash(topic) + i) % 1000
        width, height = 800, 600
        
        images.append({
            "url": f"{base_url}/id/{img_id}/{width}/{height}",
            "alt": f"{topic} illustration",
            "caption": f"Illustration related to {topic.capitalize()}",
        })
    
    return images

def get_topic_related_images(topic: str, count: int = 6) -> List[Dict[str, str]]:
    """
    Get images related to the topic using available APIs.
    
    Args:
        topic: The topic to search images for
        count: Number of images to return
        
    Returns:
        List of dictionaries with image information
    """
    # Try Unsplash first
    images = search_unsplash_images(topic, count // 2)
    
    # Try Pexels for the remaining images
    if len(images) < count:
        images.extend(search_pexels_images(topic, count - len(images)))
    
    # Fall back to placeholders if needed
    if len(images) < count:
        images.extend(get_placeholder_images(topic, count - len(images)))
    
    return images[:count]

def extract_topics_for_images(report_text: str) -> List[str]:
    """
    Extract relevant topics for images from the report text.
    
    Args:
        report_text: The report text to extract topics from
        
    Returns:
        List of topics for image search
    """
    # Look for section titles, which are often good topics for images
    section_pattern = r'(?:\*\*|##)\s*([A-Z][^*#]+?)(?:\*\*|##)'
    
    topics = []
    
    # Extract section titles
    section_matches = re.finditer(section_pattern, report_text)
    for match in section_matches:
        topic = match.group(1).strip()
        if 3 < len(topic) < 30 and not any(x in topic.lower() for x in ["reference", "conclusion", "introduction"]):
            topics.append(topic)
    
    # If we don't have enough topics, look for capitalized phrases
    if len(topics) < 3:
        topic_pattern = r'([A-Z][a-z]+(?:\s+[a-z]+){0,2})'
        topic_matches = re.finditer(topic_pattern, report_text)
        for match in topic_matches:
            topic = match.group(1).strip()
            if 3 < len(topic) < 30 and topic not in topics:
                topics.append(topic)
    
    # Limit to 3 topics and make sure main topic is included
    return list(set(topics))[:3] 