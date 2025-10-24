#!/bin/bash
# Fix and re-run multi-collection vector tests
# This will test all 5 limits correctly

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║      FIX MULTI-COLLECTION VECTOR TESTS - RE-RUN ALL 5 LIMITS        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Function to update locustfile limit
update_vector_limit() {
    local limit=$1
    python3 << PYEOF
import re
with open('locustfile_vector.py', 'r') as f:
    content = f.read()

# Replace limit = any_number with limit = $limit
content = re.sub(r'limit\s*=\s*\d+', f'limit = $limit', content)

with open('locustfile_vector.py', 'w') as f:
    f.write(content)
PYEOF
}

# Check if query files exist
if [ ! -f "queries/queries_vector_200.json" ]; then
    echo "❌ Query files not found in queries/ folder"
    echo "   Please ensure queries/queries_vector_*.json files exist"
    exit 1
fi

echo "✅ Query files found"
echo ""

# Run tests for each limit
for LIMIT in 10 50 100 150 200; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 Testing LIMIT $LIMIT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Update locustfile to use correct limit
    echo "Updating locustfile_vector.py to use limit $LIMIT..."
    update_vector_limit $LIMIT
    
    # Copy correct query file to root (where locustfile looks)
    echo "Copying queries/queries_vector_${LIMIT}.json to current directory..."
    cp "queries/queries_vector_${LIMIT}.json" "queries_vector_${LIMIT}.json"
    
    # Run test
    echo "Running test (100 users, 5 min)..."
    locust -f locustfile_vector.py \
        --users 100 \
        --spawn-rate 5 \
        --run-time 5m \
        --headless \
        --html "2ndIterQueries/reports_${LIMIT}/vector_report.html" \
        --csv "2ndIterQueries/reports_${LIMIT}/vector"
    
    echo ""
    echo "✅ Limit $LIMIT complete"
    
    # Clean up
    rm -f "queries_vector_${LIMIT}.json"
    
    if [ "$LIMIT" != "200" ]; then
        echo ""
        echo "⏸️  Pausing 10 seconds before next test..."
        sleep 10
        echo ""
    fi
done

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ ALL MULTI-COLLECTION VECTOR TESTS COMPLETE!          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Results saved to: 2ndIterQueries/reports_*/vector_*"
echo ""
echo "Next step: Regenerate combined report"
echo "   python generate_combined_report.py"
echo ""

