#!/bin/bash

# Presentation runner using reveal-md
# Usage: ./run.sh [presentation.md]

PRESENTATION="${1:-presentation-german.md}"
THEME="theme-programmy.css"

# Check if reveal-md is installed
if ! command -v reveal-md &> /dev/null; then
    echo "reveal-md not found. Installing..."
    npm install -g reveal-md
fi

echo "Starting presentation: $PRESENTATION"
echo "Theme: $THEME"
echo ""

reveal-md "$PRESENTATION" --css "$THEME" --theme black
