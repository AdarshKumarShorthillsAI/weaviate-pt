"""
Locust test for TAX queries using BM25 search.
Loads tax-specific query files.
"""

import json
import random
from locust import HttpUser, task, between, events
import config

QUERIES = []
LIMIT = 200  # Will be updated by script


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES, LIMIT
    filename = f"queries_tax_bm25_{LIMIT}.json"
    
    print("=" * 70)
    print(f"Loading: {filename}")
    print("=" * 70)
    
    try:
        with open(filename, "r") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} tax queries")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Failed to load {filename}: {e}")
        print("=" * 70)


class TaxBM25User(HttpUser):
    # wait_time = between(1, 3)
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
            name="Tax_BM25_Search"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" not in result:
                    response.success()
                else:
                    response.failure(f"GraphQL errors")
            else:
                response.failure(f"HTTP {response.status_code}")

