"""
PARALLEL HYBRID SEARCH (Alpha=0.1) - Locust performance testing for Weaviate
Sends 9 PARALLEL hybrid requests with alpha=0.1 (90% vector, 10% BM25)

Usage:
    locust -f locustfile_hybrid_01.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import json
import random
import time
from locust import HttpUser, task, events
import config

# Gevent for parallel execution
import gevent
from gevent import monkey
monkey.patch_all()


QUERIES = []
COLLECTIONS = [
    'SongLyrics', 'SongLyrics_400k', 'SongLyrics_200k',
    'SongLyrics_50k', 'SongLyrics_30k', 'SongLyrics_20k',
    'SongLyrics_15k', 'SongLyrics_12k', 'SongLyrics_10k'
]


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel hybrid (alpha=0.1) query file when Locust starts"""
    global QUERIES
    
    filename = "queries/queries_hybrid_01_200.json"
    
    print("=" * 80)
    print("🚀 PARALLEL HYBRID SEARCH TEST (Alpha=0.1)")
    print("=" * 80)
    print(f"Loading: {filename}")
    print(f"Execution: 9 parallel requests (one per collection)")
    print(f"Collections: {', '.join(COLLECTIONS)}")
    print(f"Weight: 90% vector + 10% BM25")
    print("=" * 80)
    
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✅ Loaded {len(QUERIES)} query sets")
        print(f"   Each set contains 9 individual queries (one per collection)")
        print(f"   Total individual queries: {len(QUERIES) * 9}")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("   Run: python generate_parallel_queries.py --search-types hybrid_01")
        print("=" * 80)


class ParallelHybrid01User(HttpUser):
    """Simulates a user performing parallel hybrid (0.1) searches across 9 collections"""
    
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Setup headers"""
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    def execute_single_query(self, query_data):
        """Execute a single GraphQL query and return result"""
        try:
            response = self.client.post(
                "/v1/graphql",
                headers=self.headers,
                json={"query": query_data["graphql"]},
                timeout=30,
                name=f"Parallel_Hybrid01_{query_data['collection']}"
            )
            
            return {
                "collection": query_data["collection"],
                "status_code": response.status_code,
                "response": response,
                "success": response.status_code == 200 and "errors" not in response.json()
            }
        except Exception as e:
            return {
                "collection": query_data["collection"],
                "status_code": 0,
                "response": None,
                "success": False,
                "error": str(e)
            }
    
    @task
    def parallel_search_all_collections(self):
        """Execute parallel hybrid (0.1) search across all 9 collections"""
        if not QUERIES:
            return
        
        # Pick random query set (contains 9 individual queries)
        query_set = random.choice(QUERIES)
        queries = query_set["queries"]  # List of 9 queries
        
        start_time = time.time()
        
        # Spawn 9 greenlets (one per collection) for parallel execution
        greenlets = []
        for query_data in queries:
            greenlet = gevent.spawn(self.execute_single_query, query_data)
            greenlets.append(greenlet)
        
        # Wait for ALL 9 requests to complete (with 30s timeout)
        gevent.joinall(greenlets, timeout=30)
        
        # Calculate total time
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Gather results
        results = [g.value for g in greenlets if g.value]
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        # Report to Locust
        if successful == 9:
            # All 9 collections succeeded
            events.request.fire(
                request_type="PARALLEL",
                name="Parallel_Hybrid01_All_9_Collections",
                response_time=total_time,
                response_length=0,
                exception=None,
                context={}
            )
        elif successful > 0:
            # Partial success
            events.request.fire(
                request_type="PARTIAL",
                name=f"Parallel_Hybrid01_Partial_{successful}_of_9",
                response_time=total_time,
                response_length=0,
                exception=Exception(f"Only {successful}/9 collections succeeded"),
                context={}
            )
        else:
            # Complete failure
            events.request.fire(
                request_type="FAILED",
                name="Parallel_Hybrid01_All_Failed",
                response_time=total_time,
                response_length=0,
                exception=Exception("All 9 collections failed"),
                context={}
            )

