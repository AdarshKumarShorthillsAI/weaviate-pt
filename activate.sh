#!/bin/bash
# Quick activation script for the virtual environment

cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "Current directory: $(pwd)"
echo ""
echo "Available commands:"
echo "  python verify_setup.py    - Test connections"
echo "  python process_lyrics.py  - Start processing"
echo "  python check_progress.py  - Check progress"
echo ""
echo "To deactivate: type 'deactivate'"

