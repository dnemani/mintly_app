#!/usr/bin/env python3
"""
Standalone Dash app runner
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.dash_reports import dash_app

if __name__ == '__main__':
    # Run the Dash app
    dash_app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=False
    )
