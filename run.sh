#!/bin/bash

# Check if virtual environment directory exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi

# Run the main file
if [ -f "src/main.py" ]; then
    echo "Running main file..."
    python src/main.py
else
    echo "Main file not found. Ensure src/main.py exists."
fi

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate
