#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt > /dev/null
else
    echo "Warning: requirements.txt not found. Ensuring Flask is installed..."
    pip install Flask > /dev/null
fi

# Run the application
echo "Starting Bilingual Ebook Aligner on http://127.0.0.1:8080"
python3 app.py
