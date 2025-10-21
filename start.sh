#!/bin/bash
# Startup script for Affiliate Marketing Hub

echo "Starting Affiliate Marketing Hub..."
echo "=================================="
echo ""

# Check if dependencies are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo ""
fi

# Start the application
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
