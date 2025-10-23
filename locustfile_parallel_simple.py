"""
Simple parallel Locust test - sends 9 async requests (one per collection) in parallel.
No comparison, just pure parallel testing using asyncio + aiohttp.

Usage:
    locust -f locustfile_parallel_simple.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import json
import random
import time
import aiohttp
import asyncio
from locust import HttpUser, task, between, events
import config


QUERIES_PARALLEL = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel query file"""
    global QUERIES_PARALLEL
    
    # Load BM25 queries by default (change filename as needed)
    limit = 200
    filename = f"queries_parallel_bm25_{limit}.json"
    
    print("=" * 70)
    print(f"Loading: {filename}")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES_PARALLEL = json.load(f)
        print(f"✓ Loaded {len(QUERIES_PARALLEL)} queries")
        print(f"  Each query has {len(QUERIES_PARALLEL[0]['queries'])} separate requests")
        print(f"  Parallel execution using asyncio.gather()")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("   Run: python generate_parallel_queries.py")
        print("=" * 70)


# Global event loop for reuse
_event_loop = None


def get_or_create_loop():
    """Get existing event loop or create new one for async operations"""
    global _event_loop
    
    if _event_loop is None or _event_loop.is_closed():
        _event_loop = asyncio.new_event_loop()
    
    return _event_loop


class WeaviateParallelUser(HttpUser):
    """User that sends 9 parallel async requests to collections"""
    
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Setup headers"""
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def parallel_search(self):
        """
        Send 9 parallel requests using asyncio.gather() and aiohttp.
        Measures total time for all 9 collections to complete.
        """
        if not QUERIES_PARALLEL:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_PARALLEL)
        
        async def execute_parallel_requests():
            """Execute all 9 requests in parallel"""
            
            async def send_request(session, query_info, index):
                """Send single async request"""
                collection = query_info["collection"]
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
                                return {
                                    "status": "success",
                                    "collection": collection,
                                    "data": result,
                                    "index": index
                                }
                        return {"status": "error", "collection": collection, "index": index}
                except Exception as e:
                    return {"status": "error", "collection": collection, "error": str(e), "index": index}
            
            # Create session and send all requests in parallel
            async with aiohttp.ClientSession() as session:
                # Create 9 tasks
                tasks = [
                    send_request(session, query_info, i)
                    for i, query_info in enumerate(query_data["queries"])
                ]
                
                # Execute all in parallel using asyncio.gather
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                return results
        
        # Measure total time
        start_time = time.time()
        
        # Run async function in separate thread with its own event loop
        import concurrent.futures
        
        def run_in_new_loop():
            """Run coroutine in a new event loop (separate thread)"""
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(execute_parallel_requests())
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_in_new_loop)
            results = future.result()
        
        # Calculate batch time
        batch_time = (time.time() - start_time) * 1000
        
        # Count successes
        successes = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        
        # Report to Locust
        self.environment.events.request.fire(
            request_type="POST",
            name="Parallel_9_Collections_AsyncIO",
            response_time=batch_time,
            response_length=0,
            exception=None if successes == 9 else Exception(f"{successes}/9 succeeded"),
            context={}
        )

