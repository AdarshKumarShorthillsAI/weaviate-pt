#!/bin/bash

# Create simplified tax locustfiles by copying and modifying existing ones

# Copy and modify for hybrid 01
cat > locustfile_tax_hybrid_01.py << 'PYEOF'
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
    wait_time = between(1, 3)
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
PYEOF

echo "✓ Created locustfile_tax_hybrid_01.py"

# Similar for hybrid 09
cat > locustfile_tax_hybrid_09.py << 'PYEOF'
import json, random
from locust import HttpUser, task, between, events
import config

QUERIES, LIMIT = [], 200

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES, LIMIT
    try:
        with open(f"queries_tax_hybrid_09_{LIMIT}.json") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} tax hybrid 0.9 queries")
    except Exception as e:
        print(f"❌ Failed: {e}")

class TaxHybrid09User(HttpUser):
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search(self):
        if QUERIES:
            query = random.choice(QUERIES)
            self.client.post("/v1/graphql", headers=self.headers, json={"query": query["graphql"]}, name="Tax_Hybrid09")
PYEOF

echo "✓ Created locustfile_tax_hybrid_09.py"

# Vector
cat > locustfile_tax_vector.py << 'PYEOF'
import json, random
from locust import HttpUser, task, between, events
import config

QUERIES, LIMIT = [], 200

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES, LIMIT
    try:
        with open(f"queries_tax_vector_{LIMIT}.json") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} tax vector queries")
    except Exception as e:
        print(f"❌ Failed: {e}")

class TaxVectorUser(HttpUser):
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search(self):
        if QUERIES:
            query = random.choice(QUERIES)
            self.client.post("/v1/graphql", headers=self.headers, json={"query": query["graphql"]}, name="Tax_Vector")
PYEOF

echo "✓ Created locustfile_tax_vector.py"

# Mixed
cat > locustfile_tax_mixed.py << 'PYEOF'
import json, random
from locust import HttpUser, task, between, events
import config

QUERIES, LIMIT = [], 200

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global QUERIES, LIMIT
    try:
        with open(f"queries_tax_mixed_{LIMIT}.json") as f:
            QUERIES = json.load(f)
        print(f"✓ Loaded {len(QUERIES)} tax mixed queries")
    except Exception as e:
        print(f"❌ Failed: {e}")

class TaxMixedUser(HttpUser):
    wait_time = between(1, 3)
    host = config.WEAVIATE_URL
    
    def on_start(self):
        self.headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            self.headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
    
    @task
    def search(self):
        if QUERIES:
            query = random.choice(QUERIES)
            self.client.post("/v1/graphql", headers=self.headers, json={"query": query["graphql"]}, name="Tax_Mixed")
PYEOF

echo "✓ Created locustfile_tax_mixed.py"

echo ""
echo "✅ All 4 tax locustfiles created!"

