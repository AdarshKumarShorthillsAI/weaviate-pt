"""
FastAPI Server for Parallel Collection Testing
Uses official Weaviate async client to query 9 collections in parallel
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
import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
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


# Weaviate async client (reused across requests)
weaviate_client: Optional[weaviate.WeaviateAsyncClient] = None


@app.on_event("startup")
async def startup_event():
    """Initialize Weaviate async client on startup"""
    global weaviate_client
    
    # Parse Weaviate URL
    url = WEAVIATE_URL
    is_https = url.startswith("https://")
    url_without_protocol = url.replace("https://", "").replace("http://", "")
    
    # Split host and port
    if ":" in url_without_protocol:
        host, port = url_without_protocol.split(":")
        port = int(port)
    else:
        host = url_without_protocol
        port = 443 if is_https else 80
    
    # Configure authentication
    auth_config = None
    if WEAVIATE_API_KEY and WEAVIATE_API_KEY != "your-weaviate-api-key":
        auth_config = Auth.api_key(WEAVIATE_API_KEY)
    
    # Create async Weaviate client
    weaviate_client = weaviate.use_async_with_custom(
        http_host=host,
        http_port=port,
        http_secure=is_https,
        grpc_host=host,
        grpc_port=50051,  # Default gRPC port
        grpc_secure=is_https,
        additional_config=AdditionalConfig(
            timeout=Timeout(query=60, insert=60),
        ),
        skip_init_checks=True  # Skip gRPC health check (HTTP-only mode)
    )
    
    # Connect the client
    await weaviate_client.connect()
    
    print(f"✅ FastAPI server started")
    print(f"✅ Connected to Weaviate: {WEAVIATE_URL}")
    print(f"✅ Using official Weaviate async client")
    print(f"✅ Ready to handle parallel queries for {len(COLLECTIONS)} collections")


@app.on_event("shutdown")
async def shutdown_event():
    """Close Weaviate async client on shutdown"""
    global weaviate_client
    if weaviate_client:
        await weaviate_client.close()
    print("✅ FastAPI server shutdown complete")


async def execute_single_query(query: QueryRequest) -> QueryResult:
    """
    Execute a single GraphQL query to Weaviate using official async client
    Returns only status code and timing (not full results)
    """
    start_time = time.time()
    
    try:
        # Execute GraphQL query using Weaviate async client
        response = await weaviate_client.graphql_raw_query(query.graphql)
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Check if query was successful
        if response.errors:
            # GraphQL returned errors
            success = False
            error = f"GraphQL errors: {response.errors}"
            status_code = 400  # GraphQL error
        else:
            # Success
            success = True
            error = None
            status_code = 200
        
        return QueryResult(
            collection=query.collection,
            status_code=status_code,
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

