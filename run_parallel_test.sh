#!/bin/bash
# Run parallel Weaviate test using grequests (gevent-based)

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              PARALLEL WEAVIATE TEST (grequests)                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if grequests is installed
echo "Checking grequests installation..."
python -c "import grequests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  grequests not installed. Installing..."
    pip install grequests
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install grequests"
        exit 1
    fi
    echo "✅ grequests installed"
else
    echo "✅ grequests already installed"
fi

# Check if parallel query files exist
echo ""
echo "Checking parallel query files..."
if [ ! -f "queries_parallel_bm25_200.json" ]; then
    echo "⚠️  Parallel query files not found. Generating..."
    python generate_parallel_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate parallel queries"
        exit 1
    fi
else
    echo "✅ Query files exist"
fi

# Run the test
echo ""
echo "Starting parallel performance test..."
echo "Test: 100 users, 5 min, ramp-up 5/s"
echo "Method: 9 parallel requests per query (grequests)"
echo ""

locust -f locustfile_parallel_working.py \
    --users 100 \
    --spawn-rate 5 \
    --run-time 5m \
    --headless \
    --html parallel_test_results.html \
    --csv parallel_test_results

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE!                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Report: parallel_test_results.html"
echo "CSV: parallel_test_results_stats.csv"
echo ""

