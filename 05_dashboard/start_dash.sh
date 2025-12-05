#!/bin/bash
# Start Plotly Dash Dashboard (Fast, Modern UI)

echo "Starting RAKEZ Lead Scoring Dashboard (Plotly Dash)..."
echo ""
echo "Dashboard will be available at: http://localhost:8050"
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python dash_dashboard.py

