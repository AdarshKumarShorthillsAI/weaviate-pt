#!/bin/bash

# Run pure vector search tests across all 5 limits
# Tests nearVector (semantic search only, no BM25)

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║       PURE VECTOR SEARCH TESTS - ALL 5 LIMITS (nearVector)          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Test Configuration:"
echo "  Search Type: nearVector (pure semantic, no BM25)"
echo "  Users: 100 concurrent"
echo "  Ramp-up: 5 users/second"
echo "  Duration: 5 minutes per test"
echo "  Limits: 10, 50, 100, 150, 200"
echo "  Total time: ~25 minutes for all 5 tests"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check if query files exist
if [ ! -f "queries_vector_200.json" ]; then
    echo "⚠️  Vector query files not found. Generating..."
    python generate_vector_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate vector queries"
        exit 1
    fi
    echo ""
fi

# Create reports directory
mkdir -p vector_reports

# Test 1: Limit 10
echo "🔍 Test 1/5: nearVector Search (limit=10)"
echo "══════════════════════════════════════════════════════════════════════"

# Update locustfile to use queries_vector_10.json
sed -i.bak 's/queries_vector_[0-9]*\.json/queries_vector_10.json/' locustfile_vector.py

locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html vector_reports/vector_limit10_report.html \
    --csv vector_reports/vector_limit10

echo ""
echo "✅ Vector test (limit=10) complete"
echo "Waiting 5 seconds..."
sleep 5

# Test 2: Limit 50
echo ""
echo "🔍 Test 2/5: nearVector Search (limit=50)"
echo "══════════════════════════════════════════════════════════════════════"

sed -i.bak 's/queries_vector_[0-9]*\.json/queries_vector_50.json/' locustfile_vector.py

locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html vector_reports/vector_limit50_report.html \
    --csv vector_reports/vector_limit50

echo ""
echo "✅ Vector test (limit=50) complete"
echo "Waiting 5 seconds..."
sleep 5

# Test 3: Limit 100
echo ""
echo "🔍 Test 3/5: nearVector Search (limit=100)"
echo "══════════════════════════════════════════════════════════════════════"

sed -i.bak 's/queries_vector_[0-9]*\.json/queries_vector_100.json/' locustfile_vector.py

locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html vector_reports/vector_limit100_report.html \
    --csv vector_reports/vector_limit100

echo ""
echo "✅ Vector test (limit=100) complete"
echo "Waiting 5 seconds..."
sleep 5

# Test 4: Limit 150
echo ""
echo "🔍 Test 4/5: nearVector Search (limit=150)"
echo "══════════════════════════════════════════════════════════════════════"

sed -i.bak 's/queries_vector_[0-9]*\.json/queries_vector_150.json/' locustfile_vector.py

locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html vector_reports/vector_limit150_report.html \
    --csv vector_reports/vector_limit150

echo ""
echo "✅ Vector test (limit=150) complete"
echo "Waiting 5 seconds..."
sleep 5

# Test 5: Limit 200
echo ""
echo "🔍 Test 5/5: nearVector Search (limit=200)"
echo "══════════════════════════════════════════════════════════════════════"

sed -i.bak 's/queries_vector_[0-9]*\.json/queries_vector_200.json/' locustfile_vector.py

locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html vector_reports/vector_limit200_report.html \
    --csv vector_reports/vector_limit200

echo ""
echo "✅ Vector test (limit=200) complete"
echo ""

# Restore original
mv locustfile_vector.py.bak locustfile_vector.py 2>/dev/null || true

# Summary
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                   ALL VECTOR TESTS COMPLETE!                         ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to vector_reports/ directory:"
echo "   • vector_limit10_report.html"
echo "   • vector_limit50_report.html"
echo "   • vector_limit100_report.html"
echo "   • vector_limit150_report.html"
echo "   • vector_limit200_report.html"
echo ""
echo "   • CSV files for detailed analysis"
echo ""
echo "📈 Key Metrics:"
echo "   • Compare response times across limits"
echo "   • Check vector search performance"
echo "   • Identify HNSW index bottlenecks"
echo ""
echo "Open reports:"
echo "   open vector_reports/*.html"
echo ""

