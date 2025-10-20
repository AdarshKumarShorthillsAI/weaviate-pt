"""
Locust performance testing with PARALLEL requests.
Sends 9 separate requests (one per collection) in parallel, then merges results.
Compare this with the single multi-collection approach.

Usage:
    locust -f locustfile_parallel.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import json
import random
import asyncio
import aiohttp
from locust import HttpUser, task, between, events
import config


QUERIES_PARALLEL = []
SEARCH_TYPE = "bm25"  # Can be: bm25, hybrid_01, hybrid_09, mixed


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel query file"""
    global QUERIES_PARALLEL, SEARCH_TYPE
    
    # Determine which file to load (set this before running)
    limit = 200  # Default limit
    filename = f"queries_parallel_{SEARCH_TYPE}_{limit}.json"
    
    print("=" * 70)
    print(f"Loading parallel query file: {filename}")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES_PARALLEL = json.load(f)
        print(f"✓ Loaded {len(QUERIES_PARALLEL)} queries")
        print(f"  Each query has {len(QUERIES_PARALLEL[0]['queries'])} separate requests")
        print(f"  (One per collection - sent in parallel)")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 70)


class WeaviateParallelUser(HttpUser):
    """User that sends parallel requests to multiple collections"""
    
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Setup"""
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def parallel_search(self):
        """
        Send 9 parallel requests (one per collection) using ThreadPoolExecutor.
        Measures total time for all 9 requests to complete.
        """
        if not QUERIES_PARALLEL:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_PARALLEL)
        
        # Use ThreadPoolExecutor for true parallel requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        import requests
        
        # Track total time for parallel batch
        batch_start = time.time()
        
        def send_single_request(query_info):
            """Send single request to one collection"""
            collection_name = query_info["collection"]
            graphql = query_info["graphql"]
            
            try:
                response = requests.post(
                    f"{config.WEAVIATE_URL}/v1/graphql",
                    headers=self.headers,
                    json={"query": graphql},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "errors" not in result:
                        return ("success", collection_name, result, response.elapsed.total_seconds() * 1000)
                    else:
                        return ("error", collection_name, None, 0)
                else:
                    return ("error", collection_name, None, 0)
            except Exception as e:
                return ("error", collection_name, None, 0)
        
        # Send all 9 requests in parallel using ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=9) as executor:
            futures = [executor.submit(send_single_request, q) for q in query_data["queries"]]
            
            for future in as_completed(futures):
                status, collection, result, response_time = future.result()
                if status == "success":
                    results.append(result)
        
        # Calculate total batch time
        batch_time = (time.time() - batch_start) * 1000  # Convert to ms
        
        # Report to Locust as a single logical operation
        # This shows the TOTAL time to get results from all 9 collections
        self.environment.events.request.fire(
            request_type="POST",
            name="Parallel_All_9_Collections",
            response_time=batch_time,
            response_length=sum(len(str(r)) for r in results),
            exception=None if len(results) == 9 else Exception(f"Only got {len(results)}/9 results"),
            context={}
        )

