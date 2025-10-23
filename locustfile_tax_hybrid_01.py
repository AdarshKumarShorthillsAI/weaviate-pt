import json, random
from locust import HttpUser, task, between, events
import config

QUERIES, LIMIT = [], 200

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES, LIMIT
    try:
        with open(f"queries_tax_hybrid_01_{LIMIT}.json") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} tax hybrid 0.1 queries")
    except Exception as e:
        print(f"❌ Failed: {e}")

class TaxHybrid01User(HttpUser):
    # wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search(self):
        if QUERIES:
            query = random.choice(QUERIES)
            self.client.post("/v1/graphql", headers=self.headers, json={"query": query["graphql"]}, name="Tax_Hybrid01")
