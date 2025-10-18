"""
Locust performance testing for Weaviate.
Tests search performance across multiple collections with pre-generated queries.

Usage:
    locust -f locustfile.py --users 100 --spawn-rate 5 --run-time 5m --headless

Parameters:
    --users 100: 100 concurrent users
    --spawn-rate 5: Ramp up 5 users per second
    --run-time 5m: Run for 5 minutes
    --headless: No web UI (direct run)
"""

import json
import random
import time
from locust import HttpUser, task, between, events
import config


# Load pre-generated query files on startup
QUERIES_BM25 = []
QUERIES_HYBRID_01 = []
QUERIES_HYBRID_09 = []
QUERIES_MIXED = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load query files when Locust starts"""
    global QUERIES_BM25, QUERIES_HYBRID_01, QUERIES_HYBRID_09, QUERIES_MIXED
    
    print("=" * 70)
    print("Loading pre-generated query files...")
    print("=" * 70)
    
    try:
        with open("queries_bm25.json", "r") as f:
            QUERIES_BM25 = json.load(f)
        print(f"✓ Loaded queries_bm25.json: {len(QUERIES_BM25)} queries")
    except Exception as e:
        print(f"❌ Failed to load queries_bm25.json: {e}")
    
    try:
        with open("queries_hybrid_01.json", "r") as f:
            QUERIES_HYBRID_01 = json.load(f)
        print(f"✓ Loaded queries_hybrid_01.json: {len(QUERIES_HYBRID_01)} queries")
    except Exception as e:
        print(f"❌ Failed to load queries_hybrid_01.json: {e}")
    
    try:
        with open("queries_hybrid_09.json", "r") as f:
            QUERIES_HYBRID_09 = json.load(f)
        print(f"✓ Loaded queries_hybrid_09.json: {len(QUERIES_HYBRID_09)} queries")
    except Exception as e:
        print(f"❌ Failed to load queries_hybrid_09.json: {e}")
    
    try:
        with open("queries_mixed.json", "r") as f:
            QUERIES_MIXED = json.load(f)
        print(f"✓ Loaded queries_mixed.json: {len(QUERIES_MIXED)} queries")
    except Exception as e:
        print(f"❌ Failed to load queries_mixed.json: {e}")
    
    print("=" * 70)
    print(f"Total queries loaded: {len(QUERIES_BM25) + len(QUERIES_HYBRID_01) + len(QUERIES_HYBRID_09) + len(QUERIES_MIXED)}")
    print("=" * 70)


class WeaviateUser(HttpUser):
    """
    Simulates a user searching Weaviate.
    Each user randomly picks queries and executes them.
    """
    
    # Wait between 1-3 seconds between requests
    wait_time = between(1, 3)
    
    # Set host from config
    host = config.WEAVIATE_URL
    
    def on_start(self):
        """Called when a user starts"""
        # Setup headers
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task(25)
    def search_bm25(self):
        """
        Execute BM25 search across ALL collections in single request.
        Weight: 25 (25% of requests)
        """
        if not QUERIES_BM25:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_BM25)
        
        # Execute single GraphQL query that searches all collections
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name="BM25_All_Collections"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    response.failure(f"GraphQL errors: {result['errors']}")
                else:
                    # Count total results from all collections
                    get_data = result.get("data", {}).get("Get", {})
                    total_results = sum(len(get_data.get(coll, [])) for coll in ["SongLyrics", "SongLyrics_400k", "SongLyrics_200k", "SongLyrics_50k", "SongLyrics_30k", "SongLyrics_20k", "SongLyrics_15k", "SongLyrics_12k", "SongLyrics_10k"])
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(25)
    def search_hybrid_01(self):
        """
        Execute Hybrid search (alpha=0.1) across ALL collections in single request.
        Weight: 25 (25% of requests)
        """
        if not QUERIES_HYBRID_01:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_HYBRID_01)
        
        # Execute single GraphQL query that searches all collections
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name="Hybrid_0.1_All_Collections"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    response.failure(f"GraphQL errors: {result['errors']}")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(25)
    def search_hybrid_09(self):
        """
        Execute Hybrid search (alpha=0.9) across ALL collections in single request.
        Weight: 25 (25% of requests)
        """
        if not QUERIES_HYBRID_09:
            return
        
        # Pick random query
        query_data = random.choice(QUERIES_HYBRID_09)
        
        # Execute single GraphQL query that searches all collections
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name="Hybrid_0.9_All_Collections"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    response.failure(f"GraphQL errors: {result['errors']}")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(25)
    def search_mixed(self):
        """
        Execute mixed search types across ALL collections in single request.
        Weight: 25 (25% of requests)
        """
        if not QUERIES_MIXED:
            return
        
        # Pick random query from mixed set
        query_data = random.choice(QUERIES_MIXED)
        search_type = query_data["search_type"]
        
        # Execute single GraphQL query that searches all collections
        with self.client.post(
            "/v1/graphql",
            headers=self.headers,
            json={"query": query_data["graphql"]},
            catch_response=True,
            name=f"Mixed_{search_type}_All_Collections"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    response.failure(f"GraphQL errors: {result['errors']}")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

