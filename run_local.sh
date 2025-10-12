#!/bin/bash
# Script to run Mintly app locally

echo "🚀 Starting Mintly Budgeting App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p data logs results

# Run the application
echo "✅ Starting application on http://localhost:8000"
echo "Press Ctrl+C to stop"
python app/main.py

