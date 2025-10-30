"""
PARALLEL HYBRID 0.9 SEARCH via FastAPI - Locust performance testing

Usage:
    python fastapi_server.py  # Start server first
    locust -f locustfile_hybrid_09_fastapi.py --users 100 --spawn-rate 5 --run-time 5m --headless
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
    global QUERIES
    filename = "queries/queries_hybrid_09_200.json"
    print("=" * 80)
    print("🚀 PARALLEL HYBRID 0.9 SEARCH TEST (via FastAPI)")
    print("=" * 80)
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✅ Loaded {len(QUERIES)} query sets")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("=" * 80)

class ParallelHybrid09User(HttpUser):
    host = "http://localhost:8000"
    
    @task
    def parallel_search_via_fastapi(self):
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
            name="Parallel_Hybrid09_All_9"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                successful = result.get("successful", 0)
                if successful == 9:
                    response.success()
                elif successful > 0:
                    response.failure(f"Only {successful}/9 succeeded")
                else:
                    response.failure("All failed")
            else:
                response.failure(f"HTTP {response.status_code}")

