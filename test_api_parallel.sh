#!/bin/bash

# Test parallel search using API approach
# Starts API server, runs Locust test, then stops API

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        API-BASED PARALLEL TESTING - NO EVENT LOOP CONFLICTS!         ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
LIMIT=${1:-200}
USERS=${2:-100}
SPAWN_RATE=${3:-5}
DURATION=${4:-5m}

echo "Test Configuration:"
echo "  Limit: $LIMIT"
echo "  Users: $USERS"
echo "  Spawn rate: $SPAWN_RATE"
echo "  Duration: $DURATION"
echo "  Approach: API endpoint with asyncio.gather()"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check if query files exist
if [ ! -f "queries_parallel_bm25_${LIMIT}.json" ]; then
    echo "⚠️  Query files not found. Generating..."
    python generate_parallel_queries.py
fi

# Step 1: Start API server
echo "🚀 Step 1: Starting Parallel Search API server..."
python parallel_search_api.py &
API_PID=$!

echo "   API PID: $API_PID"
echo "   Waiting 5 seconds for API to start..."
sleep 5

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API server running on http://localhost:8000"
echo ""

# Step 2: Run Locust test
echo "🧪 Step 2: Running Locust performance test..."
echo "══════════════════════════════════════════════════════════════════════"

mkdir -p api_parallel_reports

locust -f locustfile_api.py \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time $DURATION \
    --headless \
    --html api_parallel_reports/api_parallel_limit${LIMIT}.html \
    --csv api_parallel_reports/api_parallel_limit${LIMIT}

TEST_EXIT_CODE=$?

echo ""
echo "✅ Locust test complete"
echo ""

# Step 3: Stop API server
echo "🛑 Step 3: Stopping API server..."
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null

echo "✅ API server stopped"
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                         TEST COMPLETE!                               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved:"
echo "   api_parallel_reports/api_parallel_limit${LIMIT}.html"
echo "   api_parallel_reports/api_parallel_limit${LIMIT}_stats.csv"
echo ""
echo "View results:"
echo "   open api_parallel_reports/api_parallel_limit${LIMIT}.html"
echo ""

exit $TEST_EXIT_CODE

