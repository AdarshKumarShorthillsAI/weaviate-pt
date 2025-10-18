#!/bin/bash

# Run all 4 performance tests sequentially
# Each test runs for 5 minutes with 100 users

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║      WEAVIATE PERFORMANCE TEST SUITE - ALL 4 SCENARIOS               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Test Configuration:"
echo "  Users: 100 concurrent"
echo "  Ramp-up: 5 users/second"
echo "  Duration: 5 minutes per test"
echo "  Total time: ~20 minutes for all 4 tests"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Test 1: BM25
echo "🔍 Test 1/4: BM25 Search (Pure Keyword)"
echo "══════════════════════════════════════════════════════════════════════"
locust -f locustfile_bm25.py --users 100 --spawn-rate 5 --run-time 5m --headless --html reports/bm25_report.html --csv reports/bm25
echo ""
echo "✅ BM25 test complete"
echo ""
echo "Waiting 10 seconds before next test..."
sleep 10

# Test 2: Hybrid 0.1
echo ""
echo "🔍 Test 2/4: Hybrid Search (alpha=0.1 - Keyword Focused)"
echo "══════════════════════════════════════════════════════════════════════"
locust -f locustfile_hybrid_01.py --users 100 --spawn-rate 5 --run-time 5m --headless --html reports/hybrid_01_report.html --csv reports/hybrid_01
echo ""
echo "✅ Hybrid 0.1 test complete"
echo ""
echo "Waiting 10 seconds before next test..."
sleep 10

# Test 3: Hybrid 0.9
echo ""
echo "🔍 Test 3/4: Hybrid Search (alpha=0.9 - Vector Focused)"
echo "══════════════════════════════════════════════════════════════════════"
locust -f locustfile_hybrid_09.py --users 100 --spawn-rate 5 --run-time 5m --headless --html reports/hybrid_09_report.html --csv reports/hybrid_09
echo ""
echo "✅ Hybrid 0.9 test complete"
echo ""
echo "Waiting 10 seconds before next test..."
sleep 10

# Test 4: Mixed
echo ""
echo "🔍 Test 4/4: Mixed Search Types (Realistic Workload)"
echo "══════════════════════════════════════════════════════════════════════"
locust -f locustfile_mixed.py --users 100 --spawn-rate 5 --run-time 5m --headless --html reports/mixed_report.html --csv reports/mixed
echo ""
echo "✅ Mixed test complete"
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                   ALL TESTS COMPLETE!                                ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to reports/ directory:"
echo "   • bm25_report.html - BM25 test results"
echo "   • hybrid_01_report.html - Hybrid 0.1 results"
echo "   • hybrid_09_report.html - Hybrid 0.9 results"
echo "   • mixed_report.html - Mixed workload results"
echo ""
echo "   • CSV files for detailed analysis"
echo ""
echo "Open the HTML files in your browser to see detailed charts and statistics."
echo ""

