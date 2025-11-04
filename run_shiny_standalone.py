#!/usr/bin/env python3
"""
Standalone Shiny app runner for Mintly interactive reports
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.shiny_reports import shiny_app

# Export the app for shiny run command
app = shiny_app