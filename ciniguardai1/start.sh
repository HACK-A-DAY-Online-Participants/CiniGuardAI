#!/bin/bash

# CinemaGuard Quick Start Script

echo "🎬 Starting CinemaGuard Anti-Piracy System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. Please edit it with your settings."
    echo ""
fi

# Start the server
echo "🚀 Starting server on http://localhost:8000"
echo ""
echo "Available endpoints:"
echo "  - Dashboard:    http://localhost:8000/"
echo "  - Setup Grid:   http://localhost:8000/setup"
echo "  - Live Monitor: http://localhost:8000/monitor (with RED phone indicators!)"
echo ""

uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
