# 🚀 Parallel Testing - FastAPI Approach

## 🎯 New Architecture

### **Two Approaches Available:**

#### **Approach 1: Direct Gevent (Original)**
```
Locust → Weaviate
  └─ Uses gevent to send 9 parallel HTTP requests
  └─ Returns full search results
  └─ Higher bandwidth usage
```

#### **Approach 2: FastAPI with Async Client (NEW)**
```
Locust → FastAPI → Weaviate
  └─ FastAPI uses async httpx client
  └─ Executes 9 queries in parallel using asyncio.gather
  └─ Returns ONLY status codes and timing (not full results)
  └─ Much lower bandwidth and faster
```

---

## 🏗️ FastAPI Approach Benefits

### Why Use FastAPI?

✅ **Async/Await** - True async I/O with modern Python async  
✅ **Lower Bandwidth** - Returns only metadata (status + time), not GB of results  
✅ **Faster Responses** - No need to serialize/transmit large result sets  
✅ **Better Resource Usage** - Async is more efficient than gevent  
✅ **Centralized Logic** - All parallel logic in FastAPI, Locust just calls endpoint  
✅ **Easy Monitoring** - FastAPI has built-in /docs and /health endpoints  

---

## 📂 Files Created

### FastAPI Server

```
fastapi_server.py                    - FastAPI application with async Weaviate
```

**Features:**
- Async httpx client for Weaviate
- `/parallel_query` endpoint - Execute 9 parallel queries
- `/health` endpoint - Health check
- `/docs` endpoint - Interactive API documentation
- Returns only: `{total_time_ms, successful, failed, results: [{collection, status_code, response_time_ms}]}`

### Locustfiles (FastAPI-based)

```
locustfile_vector_fastapi.py         - Vector search via FastAPI
locustfile_bm25_fastapi.py           - BM25 search via FastAPI
locustfile_hybrid_01_fastapi.py      - Hybrid α=0.1 via FastAPI
locustfile_hybrid_09_fastapi.py      - Hybrid α=0.9 via FastAPI
locustfile_mixed_fastapi.py          - Mixed search via FastAPI
```

**Features:**
- All point to `http://localhost:8000` (FastAPI)
- Send query set to `/parallel_query` endpoint
- Receive only timing and status info
- Much simpler than gevent approach

### Helper Scripts

```
start_fastapi_server.sh              - Start FastAPI server
run_parallel_tests_fastapi.sh        - Run all 5 tests via FastAPI
```

---

## 🚀 How to Use

### Step 1: Start FastAPI Server

**Terminal 1:**
```bash
cd performance_testing/parallel_testing

# Option A: Using helper script
./start_fastapi_server.sh

# Option B: Direct
python fastapi_server.py
```

**Server will start on:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`  
**Health Check:** `http://localhost:8000/health`

**Keep this terminal running during tests!**

---

### Step 2: Run Locust Tests

**Terminal 2:**
```bash
cd performance_testing/parallel_testing

# Run all 5 tests
./run_parallel_tests_fastapi.sh

# Or run individual test
locust -f locustfile_vector_fastapi.py --users 100 --spawn-rate 5 --run-time 5m --headless
```

---

### Step 3: Stop Server (When Done)

In Terminal 1 (where FastAPI is running):
```
Press Ctrl+C
```

---

## 📊 API Response Format

### Request to FastAPI:
```json
POST /parallel_query
{
  "query_text": "love and heartbreak",
  "search_type": "vector",
  "queries": [
    {
      "collection": "SongLyrics",
      "graphql": "{ Get { SongLyrics(nearVector: {...}) {...} } }"
    },
    ... (8 more collections)
  ]
}
```

### Response from FastAPI:
```json
{
  "total_time_ms": 823.45,
  "successful": 9,
  "failed": 0,
  "results": [
    {
      "collection": "SongLyrics",
      "status_code": 200,
      "response_time_ms": 801.23,
      "success": true,
      "error": null
    },
    {
      "collection": "SongLyrics_400k",
      "status_code": 200,
      "response_time_ms": 412.56,
      "success": true,
      "error": null
    },
    ... (7 more)
  ]
}
```

**Note:** No actual search results returned - only metadata!

---

## 🔄 Comparison: Gevent vs FastAPI

| Aspect | Gevent Approach | FastAPI Approach |
|--------|-----------------|------------------|
| **Parallelization** | gevent.spawn() | asyncio.gather() |
| **HTTP Client** | Locust's client | httpx.AsyncClient |
| **Response Size** | Full results (GB) | Metadata only (KB) |
| **Bandwidth** | High | Low ✅ |
| **Complexity** | Medium | Low ✅ |
| **Monitoring** | Limited | Built-in /docs ✅ |
| **Resource Usage** | Moderate | Lower ✅ |
| **Speed** | Fast | Faster ✅ |

---

## 📁 File Organization

### **Original Gevent Approach:**
```
locustfile_vector.py                 - Direct to Weaviate (gevent)
locustfile_bm25.py                   - Direct to Weaviate (gevent)
locustfile_hybrid_01.py              - Direct to Weaviate (gevent)
locustfile_hybrid_09.py              - Direct to Weaviate (gevent)
locustfile_mixed.py                  - Direct to Weaviate (gevent)
run_parallel_tests.sh                - Run original tests
```

### **New FastAPI Approach:**
```
fastapi_server.py                    - FastAPI server ⭐ NEW
locustfile_vector_fastapi.py         - Via FastAPI ⭐ NEW
locustfile_bm25_fastapi.py           - Via FastAPI ⭐ NEW
locustfile_hybrid_01_fastapi.py      - Via FastAPI ⭐ NEW
locustfile_hybrid_09_fastapi.py      - Via FastAPI ⭐ NEW
locustfile_mixed_fastapi.py          - Via FastAPI ⭐ NEW
start_fastapi_server.sh              - Helper script ⭐ NEW
run_parallel_tests_fastapi.sh        - Run FastAPI tests ⭐ NEW
```

**Both approaches available!** You can test and compare both.

---

## 🎯 When to Use Each Approach

### Use **Gevent Approach** when:
- You want direct Weaviate testing
- You need to test Weaviate's direct HTTP performance
- You want to see full search results
- You're testing Weaviate infrastructure limits

### Use **FastAPI Approach** when:
- You want realistic production architecture
- You need lower bandwidth (return only metadata)
- You want faster test execution
- You're testing API layer performance
- You want better monitoring (/docs endpoint)

---

## 🧪 Quick Test (FastAPI Approach)

### Start Server:
```bash
cd performance_testing/parallel_testing
./start_fastapi_server.sh
```

### In Another Terminal, Test It:
```bash
cd performance_testing/parallel_testing

# Quick 30-second test
locust -f locustfile_vector_fastapi.py --users 10 --spawn-rate 2 --run-time 30s --headless
```

### Check API Docs:
```bash
open http://localhost:8000/docs
```

You'll see interactive API documentation where you can test the endpoint manually!

---

## 📊 Expected Performance

### Response Times:

**Gevent Approach (returns full results):**
- Total response: ~2-5 MB per request
- Network time: Significant
- Response time: Dominated by data transfer

**FastAPI Approach (returns only metadata):**
- Total response: ~2-5 KB per request (1000x smaller!)
- Network time: Minimal
- Response time: Dominated by query execution (true performance)

**Expected:** FastAPI approach should be **significantly faster** due to lower bandwidth!

---

## 🔧 Dependencies

### Required (already in requirements.txt):
```
fastapi>=0.104.0          ✅ Already present
uvicorn>=0.24.0          ✅ Already present
httpx                     ⚠️  Need to add
```

### Install Missing:
```bash
pip install httpx
```

Or add to `requirements.txt`:
```
httpx>=0.25.0
```

---

## 🚀 Complete Workflow

### 1. Start FastAPI Server (Terminal 1)
```bash
cd /path/to/nthScaling/performance_testing/parallel_testing
./start_fastapi_server.sh
```

Wait for: `✅ FastAPI server started`

### 2. Run Tests (Terminal 2)
```bash
cd /path/to/nthScaling/performance_testing/parallel_testing

# All 5 tests
./run_parallel_tests_fastapi.sh

# Or specific test
locust -f locustfile_vector_fastapi.py --users 100 --run-time 5m --headless
```

### 3. Generate Report (Terminal 2)
```bash
python generate_parallel_report.py results_fastapi_YYYYMMDD_HHMMSS
```

### 4. Stop Server (Terminal 1)
```
Press Ctrl+C
```

---

## 🎯 Key Differences

### What FastAPI Does:

1. **Receives** query set from Locust (9 queries)
2. **Executes** all 9 in parallel using `asyncio.gather()`
3. **Returns** only:
   - Total time for all 9
   - Success count
   - Failure count
   - Per-collection: status code + response time

### What FastAPI Does NOT Do:

❌ Does NOT return search results (titles, lyrics, etc.)  
❌ Does NOT serialize large result sets  
❌ Does NOT transfer GB of data  

### Result:

✅ **Much faster responses** (KB instead of MB)  
✅ **True performance testing** (measures query time, not data transfer time)  
✅ **Realistic production architecture** (API layer pattern)  

---

## 📝 Notes

### Both Approaches Valid

- **Keep gevent files** - For direct Weaviate testing
- **Use FastAPI files** - For realistic API performance testing
- **Compare results** - See which architecture is faster

### FastAPI Server State

- Server maintains async HTTP client (connection pooling)
- Reuses connections across requests (efficient)
- Can handle high concurrency (async I/O)

### Monitoring

Visit `http://localhost:8000/docs` while server is running for:
- Interactive API documentation
- Test endpoint manually
- See request/response schemas
- Try different query sets

---

## 🎉 Summary

**New FastAPI approach provides:**
- ✅ Modern async Python architecture
- ✅ Lower bandwidth usage
- ✅ Faster response times
- ✅ Better monitoring capabilities
- ✅ Realistic production pattern

**Original gevent approach still available for:**
- ✅ Direct Weaviate testing
- ✅ Infrastructure stress testing
- ✅ Comparison benchmarks

**Use both and compare!** 🚀

