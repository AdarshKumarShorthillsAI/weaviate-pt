#!/bin/bash

# Test ONLY the parallel approach across all 9 collections
# Simplified - no comparison, just parallel testing

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         PARALLEL ASYNC TESTING - 9 Collections in Parallel          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
LIMIT=${1:-200}  # Default to 200, or use first argument
USERS=${2:-100}  # Default to 100 users
SPAWN_RATE=${3:-5}  # Default to 5 users/second
DURATION=${4:-5m}  # Default to 5 minutes

echo "Test Configuration:"
echo "  Limit: $LIMIT results per collection"
echo "  Users: $USERS concurrent"
echo "  Spawn rate: $SPAWN_RATE users/second"  
echo "  Duration: $DURATION"
echo "  Approach: asyncio.gather() - 9 parallel async requests"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Generate parallel queries if not exist
if [ ! -f "queries_parallel_bm25_${LIMIT}.json" ]; then
    echo "📝 Generating parallel query files for limit ${LIMIT}..."
    python generate_parallel_queries.py
    echo ""
fi

# Create reports folder
mkdir -p parallel_reports

# Run parallel test
echo "🚀 Running Parallel AsyncIO Test"
echo "══════════════════════════════════════════════════════════════════════"
echo "Method: 9 async requests using asyncio.gather() + aiohttp"
echo ""

locust -f locustfile_parallel_simple.py \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time $DURATION \
    --headless \
    --html parallel_reports/parallel_async_limit${LIMIT}.html \
    --csv parallel_reports/parallel_async_limit${LIMIT}

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      TEST COMPLETE!                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved:"
echo "   parallel_reports/parallel_async_limit${LIMIT}.html"
echo "   parallel_reports/parallel_async_limit${LIMIT}_stats.csv"
echo ""
echo "📈 Key Metrics to Check:"
echo "   • Average Response Time (should be ~40-60ms)"
echo "   • 95th Percentile (consistency)"
echo "   • Throughput (requests/second)"
echo "   • Failure Rate (should be < 1%)"
echo ""
echo "Open report:"
echo "   open parallel_reports/parallel_async_limit${LIMIT}.html"
echo ""

