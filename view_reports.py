#!/usr/bin/env python3
"""
Script to view the generated HTML reports.
This will start a simple HTTP server to view the reports in a browser.
"""

import os
import sys
import webbrowser
import http.server
import socketserver
import argparse
import glob
from pathlib import Path

def get_latest_report(reports_dir):
    """Get the path to the latest HTML report in the reports directory."""
    html_files = glob.glob(os.path.join(reports_dir, "*.html"))
    if not html_files:
        return None
    
    # Sort by modification time (newest first)
    html_files.sort(key=os.path.getmtime, reverse=True)
    return html_files[0]

def main():
    parser = argparse.ArgumentParser(description="View the generated HTML reports.")
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port to run the HTTP server on (default: 8000)"
    )
    parser.add_argument(
        "--reports-dir", type=str, default="reports",
        help="Directory containing the reports (default: reports)"
    )
    parser.add_argument(
        "--report", type=str, default=None,
        help="Specific report to view (default: latest)"
    )
    
    args = parser.parse_args()
    
    # Get the absolute path to the reports directory
    reports_dir = os.path.abspath(args.reports_dir)
    
    # Check if the reports directory exists
    if not os.path.isdir(reports_dir):
        print(f"Error: Reports directory '{reports_dir}' does not exist.")
        return 1
    
    # Get the report to view
    if args.report:
        report_path = os.path.join(reports_dir, args.report)
        if not os.path.isfile(report_path):
            print(f"Error: Report '{args.report}' does not exist.")
            return 1
    else:
        report_path = get_latest_report(reports_dir)
        if not report_path:
            print(f"Error: No HTML reports found in '{reports_dir}'.")
            return 1
    
    # Get the relative path for the browser
    relative_path = os.path.relpath(report_path, os.getcwd())
    
    # Start the HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Use the current working directory as the web root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Starting HTTP server at http://localhost:{args.port}")
        print(f"Serving report: {os.path.basename(report_path)}")
        
        # Open the browser to the report
        webbrowser.open(f"http://localhost:{args.port}/{relative_path}")
        
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 