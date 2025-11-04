#!/usr/bin/env python3
"""
Standalone Streamlit app runner for Mintly interactive reports

Run with: streamlit run run_streamlit_standalone.py --server.port 8052 --server.address 0.0.0.0
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import and run the Streamlit app
from app.streamlit_reports import main

if __name__ == "__main__":
    main()
