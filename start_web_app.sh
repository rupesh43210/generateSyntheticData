#!/bin/bash
# Start script for PII Generator Web Application

echo "🚀 Starting PII Generator Web Application..."
echo ""
echo "📦 Installing dependencies if needed..."
pip install -q flask flask-cors

echo ""
echo "🌐 Starting web server on http://localhost:8080"
echo "   Press Ctrl+C to stop the server"
echo ""

python web_app.py