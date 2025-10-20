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
        Send 9 parallel requests (one per collection) using asyncio + aiohttp.
        True async parallelization - much more efficient than threads!
        """
        if not QUERIES_PARALLEL:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_PARALLEL)
        
        # Use asyncio for true async parallel requests
        import time
        import aiohttp
        
        async def send_all_requests():
            """Send all 9 requests in parallel using asyncio.gather"""
            
            async def send_single_request(session, query_info):
                """Send single async request to one collection"""
                collection_name = query_info["collection"]
                graphql = query_info["graphql"]
                
                try:
                    async with session.post(
                        f"{config.WEAVIATE_URL}/v1/graphql",
                        headers=self.headers,
                        json={"query": graphql},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "errors" not in result:
                                return ("success", collection_name, result)
                            else:
                                return ("error", collection_name, None)
                        else:
                            return ("error", collection_name, None)
                except Exception as e:
                    return ("error", collection_name, None)
            
            # Create aiohttp session
            async with aiohttp.ClientSession() as session:
                # Create tasks for all 9 collections
                tasks = [
                    send_single_request(session, query_info)
                    for query_info in query_data["queries"]
                ]
                
                # Execute all 9 requests in parallel using asyncio.gather
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                return results
        
        # Track total time for parallel batch
        batch_start = time.time()
        
        # Run async function
        results = asyncio.run(send_all_requests())
        
        # Calculate total batch time
        batch_time = (time.time() - batch_start) * 1000  # Convert to ms
        
        # Count successes
        successful_results = [r for r in results if isinstance(r, tuple) and r[0] == "success"]
        
        # Report to Locust as a single logical operation
        # This shows the TOTAL time to get results from all 9 collections using asyncio
        self.environment.events.request.fire(
            request_type="POST",
            name="Async_Parallel_All_9_Collections",
            response_time=batch_time,
            response_length=sum(len(str(r[2])) for r in successful_results if len(r) > 2),
            exception=None if len(successful_results) == 9 else Exception(f"Only {len(successful_results)}/9 succeeded"),
            context={}
        )

