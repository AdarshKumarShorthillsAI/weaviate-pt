#!/bin/bash

# Run ALL search types with TAX-RELATED queries
# Tests: BM25, Hybrid 0.1, Hybrid 0.9, nearVector (no parallel)
# 4 search types × 5 limits = 20 total tests

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║    TAX QUERY PERFORMANCE TESTS - ALL SEARCH TYPES & LIMITS           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Test Configuration:"
echo "  Query theme: Tax and compliance related (30 queries)"
echo "  Search types: BM25, Hybrid 0.1, Hybrid 0.9, nearVector, Mixed"
echo "  Limits: 10, 50, 100, 150, 200"
echo "  Users: 100 concurrent per test"
echo "  Duration: 5 minutes per test"
echo "  Total tests: 25 (5 types × 5 limits)"
echo "  Total time: ~2 hours 15 minutes"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Generate tax queries if not exist
if [ ! -f "queries_tax_bm25_200.json" ]; then
    echo "📝 Generating tax query files..."
    python generate_tax_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate tax queries"
        exit 1
    fi
    echo ""
fi

# Function to update LIMIT variable in locustfile
update_limit() {
    local locustfile=$1
    local limit=$2
    
    # Update LIMIT variable using Python (works on all OS)
    python3 << PYEOF
import re

with open('$locustfile', 'r') as f:
    content = f.read()

# Replace LIMIT = any_number with LIMIT = $limit
content = re.sub(r'LIMIT\s*=\s*\d+', f'LIMIT = $limit', content)

with open('$locustfile', 'w') as f:
    f.write(content)
PYEOF
}

# Array of limits
LIMITS=(10 50 100 150 200)

# Run tests for each limit
for LIMIT in "${LIMITS[@]}"; do
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                    TESTING LIMIT: $LIMIT                                   ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    REPORT_DIR="tax_reports_${LIMIT}"
    mkdir -p "$REPORT_DIR"
    
    # Test 1: BM25
    echo "🔍 Test 1/4: BM25 (limit=$LIMIT)"
    echo "────────────────────────────────────────────────────────────────────"
    update_limit "locustfile_tax_bm25.py" "$LIMIT"
    
    locust -f locustfile_tax_bm25.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html "$REPORT_DIR/bm25_report.html" \
        --csv "$REPORT_DIR/bm25"
    
    echo "✅ BM25 complete"
    sleep 3
    
    # Test 2: Hybrid 0.1
    echo ""
    echo "🔍 Test 2/4: Hybrid α=0.1 (limit=$LIMIT)"
    echo "────────────────────────────────────────────────────────────────────"
    update_limit "locustfile_tax_hybrid_01.py" "$LIMIT"
    
    locust -f locustfile_tax_hybrid_01.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html "$REPORT_DIR/hybrid_01_report.html" \
        --csv "$REPORT_DIR/hybrid_01"
    
    echo "✅ Hybrid 0.1 complete"
    sleep 3
    
    # Test 3: Hybrid 0.9
    echo ""
    echo "🔍 Test 3/4: Hybrid α=0.9 (limit=$LIMIT)"
    echo "────────────────────────────────────────────────────────────────────"
    update_limit "locustfile_tax_hybrid_09.py" "$LIMIT"
    
    locust -f locustfile_tax_hybrid_09.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html "$REPORT_DIR/hybrid_09_report.html" \
        --csv "$REPORT_DIR/hybrid_09"
    
    echo "✅ Hybrid 0.9 complete"
    sleep 3
    
    # Test 4: Pure Vector
    echo ""
    echo "🔍 Test 4/4: nearVector (limit=$LIMIT)"
    echo "────────────────────────────────────────────────────────────────────"
    update_limit "locustfile_tax_vector.py" "$LIMIT"
    
    locust -f locustfile_tax_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html "$REPORT_DIR/vector_report.html" \
        --csv "$REPORT_DIR/vector"
    
    echo "✅ nearVector complete"
    
    if [ "$LIMIT" != "200" ]; then
        echo ""
        echo "⏸️  Limit $LIMIT complete. Waiting 10 seconds before next limit..."
        sleep 10
    fi
done

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                   ALL TAX QUERY TESTS COMPLETE!                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results organized by limit:"
for LIMIT in "${LIMITS[@]}"; do
    echo "   tax_reports_${LIMIT}/"
    echo "      • bm25_report.html"
    echo "      • hybrid_01_report.html"
    echo "      • hybrid_09_report.html"
    echo "      • vector_report.html"
    echo "      • mixed_report.html"
done
echo ""
echo "📈 Generate combined report:"
echo "   python generate_combined_tax_report.py"
echo ""
echo "✅ All 25 tests complete!"
echo "   (5 search types × 5 limits)"
echo ""

