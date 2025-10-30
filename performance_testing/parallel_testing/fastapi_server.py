"""
FastAPI Server for Parallel Collection Testing
Uses async Weaviate client to query 9 collections in parallel
Returns only status codes and timing info (not full results)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
import time
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import config

# Initialize FastAPI
app = FastAPI(title="Parallel Weaviate Testing API")

# Weaviate configuration
WEAVIATE_URL = config.WEAVIATE_URL
WEAVIATE_API_KEY = config.WEAVIATE_API_KEY

# Collections to query
COLLECTIONS = [
    'SongLyrics', 'SongLyrics_400k', 'SongLyrics_200k',
    'SongLyrics_50k', 'SongLyrics_30k', 'SongLyrics_20k',
    'SongLyrics_15k', 'SongLyrics_12k', 'SongLyrics_10k'
]


# Request/Response Models
class QueryRequest(BaseModel):
    """Single query for one collection"""
    collection: str
    graphql: str


class QuerySetRequest(BaseModel):
    """Query set containing queries for all 9 collections"""
    query_text: str
    search_type: str
    queries: List[QueryRequest]


class QueryResult(BaseModel):
    """Result for a single collection query"""
    collection: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None


class ParallelQueryResponse(BaseModel):
    """Response for parallel query execution"""
    total_time_ms: float
    successful: int
    failed: int
    results: List[QueryResult]


# Async HTTP client (reused across requests)
http_client: Optional[httpx.AsyncClient] = None


@app.on_event("startup")
async def startup_event():
    """Initialize async HTTP client on startup"""
    global http_client
    
    headers = {"Content-Type": "application/json"}
    if WEAVIATE_API_KEY and WEAVIATE_API_KEY != "your-weaviate-api-key":
        headers["Authorization"] = f"Bearer {WEAVIATE_API_KEY}"
    
    http_client = httpx.AsyncClient(
        timeout=60.0,
        headers=headers,
        limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
    )
    print(f"✅ FastAPI server started")
    print(f"✅ Connected to Weaviate: {WEAVIATE_URL}")
    print(f"✅ Ready to handle parallel queries for {len(COLLECTIONS)} collections")


@app.on_event("shutdown")
async def shutdown_event():
    """Close async HTTP client on shutdown"""
    global http_client
    if http_client:
        await http_client.aclose()
    print("✅ FastAPI server shutdown complete")


async def execute_single_query(query: QueryRequest) -> QueryResult:
    """
    Execute a single GraphQL query to Weaviate
    Returns only status code and timing (not full results)
    """
    start_time = time.time()
    
    try:
        response = await http_client.post(
            f"{WEAVIATE_URL}/v1/graphql",
            json={"query": query.graphql},
            timeout=60.0
        )
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Check if response is successful
        success = response.status_code == 200
        
        if success:
            # Also check for GraphQL errors
            try:
                data = response.json()
                if "errors" in data:
                    success = False
                    error = f"GraphQL errors: {data['errors']}"
                else:
                    error = None
            except:
                error = "Invalid JSON response"
                success = False
        else:
            error = f"HTTP {response.status_code}"
        
        return QueryResult(
            collection=query.collection,
            status_code=response.status_code,
            response_time_ms=response_time,
            success=success,
            error=error
        )
    
    except asyncio.TimeoutError:
        response_time = (time.time() - start_time) * 1000
        return QueryResult(
            collection=query.collection,
            status_code=0,
            response_time_ms=response_time,
            success=False,
            error="Timeout after 60s"
        )
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return QueryResult(
            collection=query.collection,
            status_code=0,
            response_time_ms=response_time,
            success=False,
            error=str(e)
        )


@app.post("/parallel_query", response_model=ParallelQueryResponse)
async def parallel_query(query_set: QuerySetRequest):
    """
    Execute parallel queries to all 9 collections
    Returns only status codes and timing info (not actual data)
    
    This endpoint:
    1. Receives 9 queries (one per collection)
    2. Executes all 9 in parallel using asyncio
    3. Returns timing and status for each
    4. Does NOT return actual search results (for performance)
    """
    start_time = time.time()
    
    # Execute all 9 queries in parallel using asyncio.gather
    tasks = [execute_single_query(query) for query in query_set.queries]
    results = await asyncio.gather(*tasks)
    
    total_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Count successes and failures
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    return ParallelQueryResponse(
        total_time_ms=total_time,
        successful=successful,
        failed=failed,
        results=list(results)
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "weaviate_url": WEAVIATE_URL,
        "collections": len(COLLECTIONS)
    }


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Parallel Weaviate Testing API",
        "version": "1.0",
        "endpoints": {
            "/parallel_query": "POST - Execute parallel queries to 9 collections",
            "/health": "GET - Health check",
            "/docs": "GET - Interactive API documentation"
        },
        "collections": COLLECTIONS
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 Starting FastAPI Server for Parallel Testing")
    print("=" * 80)
    print(f"Weaviate URL: {WEAVIATE_URL}")
    print(f"Collections: {len(COLLECTIONS)}")
    print(f"Server will run on: http://0.0.0.0:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("=" * 80)
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

