"""
Locust test for BM25 search on SINGLE collection (SongLyrics).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import json
import random
from locust import HttpUser, task, between, events
import config

QUERIES = []

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES
    
    # Will be updated by runner script
    filename = "queries/queries_bm25_200.json"
    
    print("=" * 70)
    print(f"Loading: {filename}")
    print(f"Testing: Single collection ({config.WEAVIATE_CLASS_NAME}) - BM25")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} BM25 queries")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 70)


class SingleBM25User(HttpUser):
    # wait_time = between(1, 3)  # Removed for max throughput
    host = config.WEAVIATE_URL
    
    def on_start(self):
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search_bm25(self):
        if not QUERIES:
            return
        
        query_data = random.choice(QUERIES)
        
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name="Single_BM25_Search"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" not in result:
                    response.success()
                else:
                    response.failure("GraphQL errors")
            else:
                response.failure(f"HTTP {response.status_code}")

