"""
Locust test for Parallel Search API.
Tests the API endpoint that handles 9 parallel async requests.
NO event loop conflicts - just HTTP calls to the API!
"""

import json
import random
from locust import HttpUser, task, between, events


QUERIES_PARALLEL = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load parallel query file"""
    global QUERIES_PARALLEL
    
    limit = 200
    filename = f"queries_parallel_bm25_{limit}.json"
    
    print("=" * 70)
    print(f"Loading: {filename}")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES_PARALLEL = json.load(f)
        print(f"✓ Loaded {len(QUERIES_PARALLEL)} queries")
        print(f"  Testing API endpoint: POST /parallel-search")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 70)


class APIUser(HttpUser):
    """
    User that tests the Parallel Search API.
    The API handles all async complexity - Locust just makes HTTP calls!
    """
    
    wait_time = between(1, 3)
    host = "http://localhost:8000"  # API endpoint (not Weaviate!)
    
    @task
    def test_parallel_search_api(self):
        """
        Call the API endpoint that handles 9 parallel searches.
        Simple HTTP POST - no async complexity in Locust!
        """
        if not QUERIES_PARALLEL:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_PARALLEL)
        
        # Prepare request for API
        api_request = {
            "queries": query_data["queries"]  # 9 queries (one per collection)
        }
        
        # Call API endpoint (simple HTTP POST)
        with self.client.post(
            "/parallel-search",
            json=api_request,
            catch_response=True,
            name="API_Total_Time"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                
                # Check if all 9 succeeded
                if result.get("successful") == 9:
                    response.success()
                    
                    # Report pure search time separately (what we really care about!)
                    timing = result.get("timing", {})
                    pure_search_time = timing.get("pure_search_time_ms", 0)
                    
                    # Fire separate event for pure Weaviate search time
                    self.environment.events.request.fire(
                        request_type="SEARCH",
                        name="Pure_Weaviate_Search_Time",
                        response_time=pure_search_time,
                        response_length=0,
                        exception=None,
                        context={}
                    )
                else:
                    response.failure(f"Only {result.get('successful')}/9 succeeded")
            else:
                response.failure(f"HTTP {response.status_code}")

