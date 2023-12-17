#!/bin/bash

# Create a Python3 virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "Error > requirements.txt not found"
fi