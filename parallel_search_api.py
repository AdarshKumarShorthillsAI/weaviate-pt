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
    
    Request body:
    {
        "queries": [
            {"collection": "SongLyrics", "graphql": "..."},
            {"collection": "SongLyrics_400k", "graphql": "..."},
            ... (9 total)
        ]
    }
    
    Returns merged results from all 9 collections.
    """
    
    async def send_single_request(session, query_info):
        """Send single async GraphQL request"""
        collection = query_info.get("collection")
        graphql = query_info.get("graphql")
        
        headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
        
        try:
            async with session.post(
                f"{config.WEAVIATE_URL}/v1/graphql",
                headers=headers,
                json={"query": graphql},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "errors" not in result:
                        return {
                            "status": "success",
                            "collection": collection,
                            "data": result
                        }
                    else:
                        return {
                            "status": "error",
                            "collection": collection,
                            "errors": result.get("errors")
                        }
                else:
                    return {
                        "status": "error",
                        "collection": collection,
                        "http_status": response.status
                    }
        except Exception as e:
            return {
                "status": "error",
                "collection": collection,
                "error": str(e)
            }
    
    # Execute all 9 requests in parallel using asyncio.gather
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_single_request(session, query_info)
            for query_info in request.queries
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Aggregate results
    successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
    errors = [r for r in results if isinstance(r, dict) and r.get("status") == "error"]
    
    return {
        "total_collections": len(request.queries),
        "successful": len(successful),
        "errors": len(errors),
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

