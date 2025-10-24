#!/bin/bash
# Run vector tests on single collection (SongLyrics) for all 5 limits

echo "Running Single Collection Vector Tests..."
echo "Collection: SongLyrics (1M objects)"
echo "Search Type: nearVector (pure semantic)"
echo ""

# Check if vector query files exist
if [ ! -f "queries_vector_200.json" ]; then
    echo "⚠️  Vector query files not found. Generating..."
    python generate_vector_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate vector queries"
        exit 1
    fi
fi

for LIMIT in 10 50 100 150 200; do
    echo "Testing limit $LIMIT..."
    
    # Update locustfile to use correct limit
    python3 << PYEOF
import re
with open('locustfile_vector.py', 'r') as f:
    content = f.read()
content = re.sub(r'limit = \d+', f'limit = $LIMIT', content)
with open('locustfile_vector.py', 'w') as f:
    f.write(content)
PYEOF
    
    locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html single2nd/reports_${LIMIT}/vector_report.html \
        --csv single2nd/reports_${LIMIT}/vector
    
    echo "✓ Limit $LIMIT complete"
    sleep 3
done

echo ""
echo "✅ All single collection vector tests complete!"
echo "Results in: single2nd/reports_*/"

