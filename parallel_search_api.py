"""
FastAPI service that handles parallel Weaviate searches.
Makes 9 async requests in parallel using asyncio.gather().
Locust tests THIS API endpoint (no event loop conflicts).
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import aiohttp
import asyncio
import json
import uvicorn
import config


app = FastAPI(title="Parallel Weaviate Search API")


class SearchRequest(BaseModel):
    """Request model for parallel search"""
    queries: List[Dict[str, Any]]  # List of 9 queries (one per collection)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Parallel Weaviate Search API"}


@app.post("/parallel-search")
async def parallel_search(request: SearchRequest):
    """
    Execute 9 Weaviate searches in parallel using asyncio.gather().
    Tracks pure search time separately from API overhead.
    
    Request body:
    {
        "queries": [
            {"collection": "SongLyrics", "graphql": "..."},
            {"collection": "SongLyrics_400k", "graphql": "..."},
            ... (9 total)
        ]
    }
    
    Returns merged results with timing breakdown.
    """
    import time
    
    # Track total API time
    api_start = time.time()
    
    async def send_single_request(session, query_info):
        """Send single async GraphQL request with timing"""
        collection = query_info.get("collection")
        graphql = query_info.get("graphql")
        
        headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
        
        # Track search time for this collection
        search_start = time.time()
        
        try:
            async with session.post(
                f"{config.WEAVIATE_URL}/v1/graphql",
                headers=headers,
                json={"query": graphql},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                search_time = (time.time() - search_start) * 1000  # ms
                
                if response.status == 200:
                    result = await response.json()
                    if "errors" not in result:
                        return {
                            "status": "success",
                            "collection": collection,
                            "search_time_ms": search_time,
                            "data": result
                        }
                    else:
                        return {
                            "status": "error",
                            "collection": collection,
                            "search_time_ms": search_time,
                            "errors": result.get("errors")
                        }
                else:
                    return {
                        "status": "error",
                        "collection": collection,
                        "search_time_ms": search_time,
                        "http_status": response.status
                    }
        except Exception as e:
            search_time = (time.time() - search_start) * 1000
            return {
                "status": "error",
                "collection": collection,
                "search_time_ms": search_time,
                "error": str(e)
            }
    
    # Track just the parallel search execution time
    search_start = time.time()
    
    # Execute all 9 requests in parallel using asyncio.gather
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_single_request(session, query_info)
            for query_info in request.queries
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Pure search time (parallel execution only)
    pure_search_time = (time.time() - search_start) * 1000  # ms
    
    # Aggregate results
    successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
    errors = [r for r in results if isinstance(r, dict) and r.get("status") == "error"]
    
    # Get max search time (slowest collection)
    max_search_time = max([r.get("search_time_ms", 0) for r in results if isinstance(r, dict)], default=0)
    
    # Total API time
    total_api_time = (time.time() - api_start) * 1000  # ms
    
    # Calculate overhead
    api_overhead = total_api_time - pure_search_time
    
    return {
        "total_collections": len(request.queries),
        "successful": len(successful),
        "errors": len(errors),
        "timing": {
            "total_api_time_ms": round(total_api_time, 2),
            "pure_search_time_ms": round(pure_search_time, 2),
            "max_collection_time_ms": round(max_search_time, 2),
            "api_overhead_ms": round(api_overhead, 2)
        },
        "results": results
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    # Test Weaviate connection
    try:
        import requests
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{config.WEAVIATE_URL}/v1/.well-known/ready", timeout=5)
        weaviate_status = "ok" if response.status_code == 200 else "error"
    except:
        weaviate_status = "error"
    
    return {
        "api_status": "ok",
        "weaviate_status": weaviate_status,
        "weaviate_url": config.WEAVIATE_URL
    }


if __name__ == "__main__":
    print("=" * 70)
    print("PARALLEL WEAVIATE SEARCH API")
    print("=" * 70)
    print(f"\nWeaviate URL: {config.WEAVIATE_URL}")
    print(f"Starting API server on: http://0.0.0.0:8000")
    print("\nEndpoints:")
    print("  GET  /         - Root")
    print("  GET  /health   - Health check")
    print("  POST /parallel-search - Execute 9 parallel searches")
    print("\n" + "=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

