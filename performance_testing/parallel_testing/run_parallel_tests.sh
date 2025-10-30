#!/bin/bash
################################################################################
# PARALLEL COLLECTION TESTING via FastAPI - Automated Test Runner
# Uses FastAPI intermediary layer with async Weaviate client
################################################################################

set -e

echo "================================================================================"
echo "🚀 PARALLEL COLLECTION TESTING"
echo "================================================================================"
echo ""
echo "This script tests parallel execution of 9 collection queries:"
echo "  • Uses FastAPI with async Weaviate client"
echo "  • Returns only status codes and timing (optimized for performance)"
echo "  • 1000x less bandwidth than returning full results"
echo ""
echo "Each test sends 9 queries in parallel via FastAPI endpoint."
echo "================================================================================"
echo ""

# Default test parameters
USERS=${USERS:-100}
SPAWN_RATE=${SPAWN_RATE:-5}
RUN_TIME=${RUN_TIME:-5m}
LIMIT=${LIMIT:-200}
FASTAPI_PORT=${FASTAPI_PORT:-8000}

echo "📋 Test Configuration:"
echo "   Users: $USERS"
echo "   Spawn Rate: $SPAWN_RATE users/sec"
echo "   Run Time: $RUN_TIME"
echo "   Result Limit: $LIMIT per collection"
echo "   FastAPI Port: $FASTAPI_PORT"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."
echo ""

# Navigate to parallel_testing directory
cd "$(dirname "$0")"

# Check if FastAPI server is running
echo "🔍 Checking if FastAPI server is running..."
if curl -s http://localhost:$FASTAPI_PORT/health > /dev/null 2>&1; then
    echo "✅ FastAPI server is running on port $FASTAPI_PORT"
else
    echo ""
    echo "❌ FastAPI server is NOT running!"
    echo ""
    echo "Please start the FastAPI server first (in another terminal):"
    echo "   cd performance_testing/parallel_testing"
    echo "   ./start_fastapi_server.sh"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Create results directory
RESULTS_DIR="results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo ""
echo "================================================================================"
echo "📁 Results will be saved to: $RESULTS_DIR/"
echo "================================================================================"
echo ""

# Function to run a test
run_test() {
    local TEST_NAME=$1
    local LOCUSTFILE=$2
    local OUTPUT_PREFIX="${RESULTS_DIR}/${TEST_NAME}_limit${LIMIT}"
    
    echo "--------------------------------------------------------------------------------"
    echo "🔥 Running: $TEST_NAME"
    echo "   Locustfile: $LOCUSTFILE"
    echo "   Output: ${OUTPUT_PREFIX}_*"
    echo "--------------------------------------------------------------------------------"
    
    locust -f "$LOCUSTFILE" \
        --users "$USERS" \
        --spawn-rate "$SPAWN_RATE" \
        --run-time "$RUN_TIME" \
        --headless \
        --html "${OUTPUT_PREFIX}_report.html" \
        --csv "${OUTPUT_PREFIX}" \
        --logfile "${OUTPUT_PREFIX}.log"
    
    echo "✅ Completed: $TEST_NAME"
    echo ""
}

# Run all tests
echo "================================================================================"
echo "🏁 Starting Test Execution via FastAPI..."
echo "================================================================================"
echo ""

run_test "1_Vector" "locustfile_vector_fastapi.py"
run_test "2_BM25" "locustfile_bm25_fastapi.py"
run_test "3_Hybrid_01" "locustfile_hybrid_01_fastapi.py"
run_test "4_Hybrid_09" "locustfile_hybrid_09_fastapi.py"
run_test "5_Mixed" "locustfile_mixed_fastapi.py"

echo "================================================================================"
echo "✅ ALL TESTS COMPLETED!"
echo "================================================================================"
echo ""
echo "📊 Results Summary:"
echo "   Location: $RESULTS_DIR/"
echo ""
echo "   HTML Reports:"
ls -lh "$RESULTS_DIR"/*.html
echo ""
echo "   CSV Stats:"
ls -lh "$RESULTS_DIR"/*.csv
echo ""
echo "   Log Files:"
ls -lh "$RESULTS_DIR"/*.log
echo ""
echo "================================================================================"
echo "🎯 Next Steps:"
echo "   1. Generate report: python generate_parallel_report.py $RESULTS_DIR"
echo "   2. Compare with direct Weaviate approach (gevent-based locustfiles)"
echo "   3. Stop FastAPI server when done (Ctrl+C in server terminal)"
echo "================================================================================"

