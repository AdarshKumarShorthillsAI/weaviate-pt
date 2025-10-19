"""
Locust performance testing for Weaviate - Hybrid Search (alpha=0.1)
Tests keyword-focused hybrid search (90% BM25, 10% vector).

Usage:
    locust -f locustfile_hybrid_01.py --users 100 --spawn-rate 5 --run-time 5m --headless
"""

import json
import random
from locust import HttpUser, task, between, events
import config


QUERIES_HYBRID_01 = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load Hybrid 0.1 query file when Locust starts"""
    global QUERIES_HYBRID_01
    
    print("=" * 70)
    print("Loading Hybrid (alpha=0.1) query file...")
    print("=" * 70)
    
    try:
        with open("queries_hybrid_01_200.json", "r") as f:
            QUERIES_HYBRID_01 = json.load(f)
        print(f"✓ Loaded query file: {len(QUERIES_HYBRID_01)} queries")
        print(f"  Search type: Hybrid (alpha=0.1 - keyword-focused)")
        print(f"  Each query searches 9 collections")
        print(f"  Returns 200 results per collection")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load queries_hybrid_01.json: {e}")
        print("   Run: python generate_test_queries.py")
        print("=" * 70)


class WeaviateHybrid01User(HttpUser):
    """Simulates a user performing Hybrid 0.1 searches"""
    
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Setup headers"""
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search_hybrid_01_all_collections(self):
        """Execute Hybrid (0.1) search across all 9 collections in single request"""
        if not QUERIES_HYBRID_01:
            return
        
        # Pick random query from 30 options
        query_data = random.choice(QUERIES_HYBRID_01)
        
        # Execute single GraphQL query that searches all collections
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name="Hybrid_0.1_Multi_Collection_Search"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    response.failure(f"GraphQL errors: {result['errors']}")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

