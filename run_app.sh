#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    uv venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    uv pip install -r requirements.txt > /dev/null
else
    echo "Warning: requirements.txt not found. Ensuring Flask is installed..."
    uv pip install Flask > /dev/null
fi

# Run the application
echo "Starting Tandem Reader on http://127.0.0.1:8080"
# Silence SyntaxWarnings from the (unmaintained) pysbd dependency on Python 3.12+.
PYTHONWARNINGS="ignore::SyntaxWarning" python3 app.py
