#!/bin/bash
# PawCare AI Launcher Script
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -f ".venv/bin/python" ]; then
    echo "Starting PawCare AI using project virtual environment..."
    ./.venv/bin/python app.py "$@"
else
    echo "Error: .venv not found in $DIR"
    exit 1
fi
