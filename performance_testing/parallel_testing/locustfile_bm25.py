"""
PARALLEL BM25 SEARCH via FastAPI - Locust performance testing
Tests parallel execution through FastAPI intermediary layer

Usage:
    # Start FastAPI server first:
    python fastapi_server.py
    
    # Then run Locust:
    locust -f locustfile_bm25_fastapi.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import json
import random
from locust import HttpUser, task, events

QUERIES = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel BM25 query file when Locust starts"""
    global QUERIES
    
    filename = "queries/queries_bm25_200.json"
    
    print("=" * 80)
    print("🚀 PARALLEL BM25 SEARCH TEST (via FastAPI)")
    print("=" * 80)
    print(f"Loading: {filename}")
    print(f"FastAPI URL: http://localhost:8000")
    print("=" * 80)
    
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✅ Loaded {len(QUERIES)} query sets")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 80)


class ParallelBM25User(HttpUser):
    """Simulates a user performing parallel BM25 searches via FastAPI"""
    
    host = "http://localhost:8000"
    
    @task
    def parallel_search_via_fastapi(self):
        """Execute parallel BM25 search via FastAPI endpoint"""
        if not QUERIES:
            return
        
        query_set = random.choice(QUERIES)
        
        with self.client.post(
            "/parallel_query",
            json={
                "query_text": query_set["query_text"],
                "search_type": query_set["search_type"],
                "queries": query_set["queries"]
            },
            catch_response=True,
            name="Parallel_BM25_All_9"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                successful = result.get("successful", 0)
                
                if successful == 9:
                    response.success()
                elif successful > 0:
                    response.failure(f"Only {successful}/9 collections succeeded")
                else:
                    response.failure("All 9 collections failed")
            else:
                response.failure(f"HTTP {response.status_code}")

