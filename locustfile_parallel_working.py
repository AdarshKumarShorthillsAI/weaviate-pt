"""
Working parallel Locust test using grequests (gevent-based).
No asyncio conflicts - uses gevent's async model which is compatible with Locust.
"""

import json
import random
import time
import grequests  # gevent-based async requests (compatible with Locust)
from locust import HttpUser, task, between, events
import config


QUERIES_PARALLEL = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel query file"""
    global QUERIES_PARALLEL
    
    limit = 200
    filename = f"queries_parallel_bm25_{limit}.json"
    
    print("=" * 70)
    print(f"Loading: {filename}")
    print("Using: grequests (gevent-based, compatible with Locust)")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES_PARALLEL = json.load(f)
        print(f"✓ Loaded {len(QUERIES_PARALLEL)} queries")
        print(f"  Each query has {len(QUERIES_PARALLEL[0]['queries'])} parallel requests")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 70)


class WeaviateParallelUser(HttpUser):
    """
    User that sends 9 parallel requests using grequests.
    grequests is built on gevent, which is what Locust uses - no conflicts!
    """
    
    #wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Setup headers"""
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def parallel_search_gevent(self):
        """
        Send 9 parallel requests using grequests (gevent-based).
        Compatible with Locust's gevent model - no event loop conflicts!
        """
        if not QUERIES_PARALLEL:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_PARALLEL)
        
        # Measure total time
        start_time = time.time()
        
        # Create 9 requests (not sent yet)
        requests_list = []
        for query_info in query_data["queries"]:
            req = grequests.post(
                f"{config.WEAVIATE_URL}/v1/graphql",
                headers=self.headers,
                json={"query": query_info["graphql"]},
                timeout=30
            )
            requests_list.append(req)
        
        # Send all 9 requests in parallel using grequests.map
        # This uses gevent greenlets (compatible with Locust!)
        responses = grequests.map(requests_list, size=9)  # size=9 means 9 concurrent
        
        # Calculate total time
        batch_time = (time.time() - start_time) * 1000  # ms
        
        # Count successes
        successes = sum(1 for r in responses if r and r.status_code == 200)
        
        # Report to Locust
        self.environment.events.request.fire(
            request_type="POST",
            name="Parallel_9_Collections_Gevent",
            response_time=batch_time,
            response_length=0,
            exception=None if successes == 9 else Exception(f"{successes}/9 succeeded"),
            context={}
        )

