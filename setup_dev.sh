#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install py2app

# Create development build
python setup.py py2app --development

echo "Development environment setup complete!"
echo "Your development build is in the dist/ directory"
