"""
PARALLEL VECTOR SEARCH - Locust performance testing via FastAPI
Uses FastAPI with async Weaviate client for true parallel execution

FastAPI returns only status codes and timing (not full results) for optimal performance

Usage:
    # Terminal 1 - Start FastAPI server:
    ./start_fastapi_server.sh
    
    # Terminal 2 - Run Locust test:
    locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import json
import random
from locust import HttpUser, task, events
import config

QUERIES = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel vector query file when Locust starts"""
    global QUERIES
    
    filename = "queries/queries_vector_200.json"
    
    print("=" * 80)
    print("🚀 PARALLEL VECTOR SEARCH TEST (via FastAPI)")
    print("=" * 80)
    print(f"Loading: {filename}")
    print(f"Execution: 9 parallel requests via FastAPI")
    print(f"FastAPI URL: http://localhost:8000")
    print("=" * 80)
    
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✅ Loaded {len(QUERIES)} query sets")
        print(f"   Each set contains 9 individual queries (one per collection)")
        print(f"   FastAPI will execute all 9 in parallel using async")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("   Run: python generate_parallel_queries.py --search-types vector")
        print("=" * 80)


class ParallelVectorUser(HttpUser):
    """Simulates a user performing parallel vector searches via FastAPI"""
    
    # Point to FastAPI server (not Weaviate directly)
    host = "http://localhost:8000"
    
    @task
    def parallel_search_via_fastapi(self):
        """Execute parallel vector search via FastAPI endpoint"""
        if not QUERIES:
            return
        
        # Pick random query set (contains 9 individual queries)
        query_set = random.choice(QUERIES)
        
        # Send to FastAPI endpoint
        # FastAPI will execute all 9 queries in parallel and return only timing/status
        with self.client.post(
            "/parallel_query",
            json={
                "query_text": query_set["query_text"],
                "search_type": query_set["search_type"],
                "queries": query_set["queries"]
            },
            catch_response=True,
            name="Parallel_Vector_All_9"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                
                # FastAPI returns: {total_time_ms, successful, failed, results[]}
                successful = result.get("successful", 0)
                failed = result.get("failed", 0)
                total_time = result.get("total_time_ms", 0)
                
                if successful == 9:
                    # All 9 collections succeeded
                    response.success()
                elif successful > 0:
                    # Partial success
                    response.failure(f"Only {successful}/9 collections succeeded")
                else:
                    # Complete failure
                    response.failure("All 9 collections failed")
            else:
                response.failure(f"HTTP {response.status_code}")

