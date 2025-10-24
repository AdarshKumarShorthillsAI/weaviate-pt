#!/bin/bash
# Run mixed tests with tax queries for all 5 limits

echo "Running Tax Query Mixed Tests..."
echo "Queries: 30 tax-related queries"
echo "Search Types: Mix of BM25, Hybrid 0.1, Hybrid 0.9"
echo ""

# Check if tax query files exist
if [ ! -f "queries_tax_mixed_200.json" ]; then
    echo "⚠️  Tax query files not found. Generating..."
    python generate_tax_queries.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate tax queries"
        exit 1
    fi
fi

for LIMIT in 10 50 100 150 200; do
    echo "Testing limit $LIMIT..."
    
    # Update locustfile to use correct limit
    python3 << PYEOF
import re
with open('locustfile_tax_mixed.py', 'r') as f:
    content = f.read()
content = re.sub(r'LIMIT\s*=\s*\d+', f'LIMIT = $LIMIT', content)
with open('locustfile_tax_mixed.py', 'w') as f:
    f.write(content)
PYEOF
    
    locust -f locustfile_tax_mixed.py --users 100 --spawn-rate 5 --run-time 5m --headless \
        --html tax_reports/tax_reports_${LIMIT}/mixed_report.html \
        --csv tax_reports/tax_reports_${LIMIT}/mixed
    
    echo "✓ Limit $LIMIT complete"
    sleep 3
done

echo ""
echo "✅ All tax mixed tests complete!"
echo "Results in: tax_reports/tax_reports_*/"

