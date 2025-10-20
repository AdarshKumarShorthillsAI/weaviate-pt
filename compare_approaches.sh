#!/bin/bash

# Compare single multi-collection query vs parallel separate queries
# Runs both approaches and saves results for comparison

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        SINGLE vs PARALLEL APPROACH - PERFORMANCE COMPARISON          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
LIMIT=200
USERS=100
SPAWN_RATE=5
DURATION="5m"

echo "Test Configuration:"
echo "  Limit: $LIMIT results per collection"
echo "  Users: $USERS concurrent"
echo "  Spawn rate: $SPAWN_RATE users/second"
echo "  Duration: $DURATION"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Step 0: Generate query files if they don't exist
echo "📝 Checking for query files..."
if [ ! -f "queries_bm25_${LIMIT}.json" ]; then
    echo "⚠️  Query files not found. Generating..."
    python generate_single_collection_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate single-collection queries"
        exit 1
    fi
fi

if [ ! -f "queries_parallel_bm25_${LIMIT}.json" ]; then
    echo "⚠️  Parallel query files not found. Generating..."
    python generate_parallel_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate parallel queries"
        exit 1
    fi
fi

echo "✅ All query files present"
echo ""

# Create comparison reports folder
mkdir -p comparison_reports

# Test 1: Single Multi-Collection Query (Current Approach)
echo "🔍 Test 1: SINGLE Multi-Collection Query"
echo "══════════════════════════════════════════════════════════════════════"
echo "Approach: One GraphQL query searches all 9 collections"
echo ""

locust -f locustfile_bm25.py \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time $DURATION \
    --headless \
    --html comparison_reports/single_approach_bm25.html \
    --csv comparison_reports/single_approach_bm25

echo ""
echo "✅ Single approach test complete"
echo ""
echo "Waiting 30 seconds before next test..."
sleep 30

# Test 2: Parallel Separate Queries (New Approach)
echo ""
echo "🔍 Test 2: PARALLEL Separate Queries"
echo "══════════════════════════════════════════════════════════════════════"
echo "Approach: 9 parallel requests (one per collection), merge results"
echo ""

locust -f locustfile_parallel.py \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time $DURATION \
    --headless \
    --html comparison_reports/parallel_approach.html \
    --csv comparison_reports/parallel_approach

echo ""
echo "✅ Parallel approach test complete"
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                      COMPARISON COMPLETE!                            ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to:"
echo "   comparison_reports/single_approach_bm25.html"
echo "   comparison_reports/parallel_approach.html"
echo ""
echo "📈 Compare the following metrics:"
echo "   • Average Response Time"
echo "   • 95th Percentile"
echo "   • Throughput (requests/second)"
echo "   • Failure Rate"
echo ""
echo "💡 Lower response time = Faster approach"
echo ""
echo "Open reports to compare:"
echo "   open comparison_reports/single_approach_bm25.html"
echo "   open comparison_reports/parallel_approach.html"
echo ""

