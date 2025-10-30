#!/bin/bash
################################################################################
# Start FastAPI Server for Parallel Testing
################################################################################

echo "================================================================================"
echo "🚀 Starting FastAPI Server for Parallel Weaviate Testing"
echo "================================================================================"
echo ""
echo "This server:"
echo "  • Uses async Weaviate client"
echo "  • Executes 9 collection queries in parallel"
echo "  • Returns only status codes and timing (not full results)"
echo "  • Much faster and lower bandwidth than returning full data"
echo ""
echo "Server will run on: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "================================================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"

# Activate venv if exists
if [ -f "../../venv/bin/activate" ]; then
    source ../../venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if FastAPI and httpx are installed
python3 -c "import fastapi; import httpx; import uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required packages..."
    pip install fastapi httpx uvicorn
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo ""
python3 fastapi_server.py

