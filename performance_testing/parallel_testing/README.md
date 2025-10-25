# 🚀 Parallel Collection Testing

This folder contains **parallel execution tests** for Weaviate performance benchmarking. Unlike multi-collection tests (which send 1 GraphQL query with 9 sub-queries), these tests send **9 separate HTTP requests simultaneously** and measure the total time.

## 🎯 Purpose

**Test Hypothesis:** *"Parallel HTTP requests to 9 collections will be faster than a single multi-collection GraphQL query because the bottleneck becomes the slowest collection, not the sum of all collections."*

### Comparison

| Approach | Method | Expected Time |
|----------|--------|---------------|
| **Multi-Collection** | 1 GraphQL request with 9 sub-queries | Sum or sequential processing time |
| **Parallel (This)** | 9 simultaneous HTTP requests | Max(slowest_collection) + overhead |

---

## 📂 Folder Structure

```
parallel_testing/
├── generate_parallel_queries.py    # Query generator (reuses ../embeddings_cache.json)
├── locustfile_vector.py            # Vector search (9 parallel requests)
├── locustfile_bm25.py              # BM25 search (9 parallel requests)
├── locustfile_hybrid_01.py         # Hybrid α=0.1 (9 parallel requests)
├── locustfile_hybrid_09.py         # Hybrid α=0.9 (9 parallel requests)
├── locustfile_mixed.py             # Mixed search types (9 parallel requests)
├── run_parallel_tests.sh           # Automated test runner
├── queries/                        # Generated query files
│   ├── queries_vector_10.json      # 30 sets × 9 queries each
│   ├── queries_vector_50.json
│   ├── queries_vector_100.json
│   ├── queries_vector_150.json
│   ├── queries_vector_200.json
│   ├── queries_bm25_*.json         # Same pattern
│   ├── queries_hybrid_01_*.json
│   ├── queries_hybrid_09_*.json
│   └── queries_mixed_*.json
└── README.md                       # This file
```

---

## 🛠️ Setup

### Step 1: Generate Query Files

```bash
cd parallel_testing
python generate_parallel_queries.py --search-types all --limits 10 50 100 150 200
```

**What this does:**
- ✅ Reuses embeddings from `../embeddings_cache.json` (no API calls!)
- ✅ Generates 25 query files (5 search types × 5 limits)
- ✅ Each file contains 30 query sets × 9 collections = 270 individual queries

**Output:**
```
📁 parallel_testing/queries/
   ├── queries_vector_10.json    (30 query sets)
   ├── queries_vector_50.json
   ... (25 files total)
```

---

## 🏃 Running Tests

### Option 1: Run All Tests (Automated)

```bash
./run_parallel_tests.sh
```

This runs all 5 search types sequentially and saves results with timestamps.

**Default settings:**
- Users: 100
- Spawn Rate: 5 users/sec
- Run Time: 5 minutes
- Limit: 200

**Customize:**
```bash
USERS=200 SPAWN_RATE=10 RUN_TIME=10m LIMIT=150 ./run_parallel_tests.sh
```

### Option 2: Run Individual Tests

```bash
# Vector search only
locust -f locustfile_vector.py --users 100 --spawn-rate 5 --run-time 5m --headless

# BM25 search only
locust -f locustfile_bm25.py --users 100 --spawn-rate 5 --run-time 5m --headless

# Hybrid alpha=0.1 only
locust -f locustfile_hybrid_01.py --users 100 --spawn-rate 5 --run-time 5m --headless

# Hybrid alpha=0.9 only
locust -f locustfile_hybrid_09.py --users 100 --spawn-rate 5 --run-time 5m --headless

# Mixed search types
locust -f locustfile_mixed.py --users 100 --spawn-rate 5 --run-time 5m --headless
```

### Option 3: Interactive Mode (with Web UI)

```bash
locust -f locustfile_vector.py
# Open http://localhost:8089 in browser
```

---

## 📊 How It Works

### Parallel Execution Flow

```python
# 1. Load query set (30 options, each with 9 individual queries)
query_set = random.choice(QUERIES)

# 2. Spawn 9 greenlets (gevent) for parallel execution
greenlets = []
for collection_query in query_set["queries"]:  # 9 iterations
    g = gevent.spawn(send_http_request, collection_query)
    greenlets.append(g)

# 3. Wait for ALL 9 to complete (30s timeout)
gevent.joinall(greenlets, timeout=30)

# 4. Measure total time (from start to last completion)
total_time = max(all_collection_response_times)

# 5. Report success/failure to Locust
if all_9_succeeded:
    report_success(total_time)
elif some_succeeded:
    report_partial_success(total_time, count)
else:
    report_failure()
```

### Query File Structure

```json
[
  {
    "query_text": "love and heartbreak",
    "search_type": "vector",
    "limit": 200,
    "queries": [
      {
        "collection": "SongLyrics",
        "graphql": "{ Get { SongLyrics(nearVector: {...}) {...} } }"
      },
      {
        "collection": "SongLyrics_400k",
        "graphql": "{ Get { SongLyrics_400k(nearVector: {...}) {...} } }"
      },
      ... (7 more collections)
    ]
  },
  ... (29 more query sets)
]
```

---

## 🔍 Metrics Tracked

### Locust Reports Include:

1. **Request Statistics:**
   - Total requests
   - Requests per second (RPS)
   - Average response time
   - Min/Max response times
   - Success rate

2. **Parallel-Specific Metrics:**
   - `Parallel_Vector_All_9_Collections` - All 9 succeeded
   - `Parallel_Vector_Partial_X_of_9` - Only X collections succeeded
   - `Parallel_Vector_All_Failed` - All 9 failed

3. **Per-Collection Tracking:**
   - Individual response times for each collection
   - Error rates per collection
   - Identify slow collections

---

## 🎯 Expected Results

### Hypothesis Validation

**If parallel is FASTER:**
- ✅ Parallel time ≈ Time of slowest collection
- ✅ Significant improvement over multi-collection approach
- ✅ Better resource utilization on Weaviate server

**If multi-collection is FASTER:**
- ❌ Parallel has too much HTTP overhead
- ❌ Weaviate already parallelizes internally
- ❌ Network latency dominates

### Example Comparison

| Test Type | Multi-Collection | Parallel | Winner |
|-----------|------------------|----------|--------|
| Vector | 2500ms | 800ms | Parallel 🏆 |
| BM25 | 1200ms | 950ms | Parallel 🏆 |
| Hybrid 0.1 | 2800ms | 1100ms | Parallel 🏆 |
| Hybrid 0.9 | 1500ms | 1000ms | Parallel 🏆 |

---

## 🚨 Error Handling

### Automatic Features:

1. **Timeout Protection:**
   - 30s timeout per parallel batch
   - Prevents hanging requests

2. **Partial Success Tracking:**
   - If 7/9 collections succeed, still recorded as partial success
   - Detailed per-collection metrics

3. **Retry Logic:**
   - Locust handles retries automatically
   - Failed requests are tracked separately

4. **Resource Cleanup:**
   - Greenlets are properly cleaned up after each batch
   - No memory leaks

---

## 🔧 Troubleshooting

### Issue: "embeddings_cache.json not found"
```bash
# Solution: Generate embeddings first
cd ../
python generate_all_queries.py --type multi --search-types vector
cd parallel_testing
```

### Issue: "All requests timing out"
- Check Weaviate is running: `curl http://20.161.96.75/v1/.well-known/ready`
- Reduce users: `--users 10`
- Increase timeout in locustfile (currently 30s)

### Issue: "Partial failures on large collections"
- Expected! Some collections are slower
- Check which collections fail consistently
- May need to optimize those collections

---

## 📈 Comparing with Multi-Collection Results

### Side-by-Side Analysis:

1. **Run multi-collection test:**
   ```bash
   cd ../multi_collection
   locust -f locustfile_vector.py --users 100 --run-time 5m --headless
   ```

2. **Run parallel test:**
   ```bash
   cd ../parallel_testing
   locust -f locustfile_vector.py --users 100 --run-time 5m --headless
   ```

3. **Compare HTML reports:**
   - Multi: `multi_collection_report.html`
   - Parallel: `results_*/1_Vector_limit200_report.html`

4. **Key metrics to compare:**
   - Average response time
   - 95th percentile response time
   - Throughput (RPS)
   - Error rate

---

## 🎓 Technical Details

### Why Gevent?

- **Async I/O:** Enables true parallel HTTP requests
- **Lightweight:** Much more efficient than threads
- **Locust Compatible:** Built-in support in Locust
- **Non-blocking:** Doesn't block on network I/O

### Collection Sizes (for reference)

| Collection | Objects | Expected Response Time |
|------------|---------|------------------------|
| SongLyrics | 1,000,000 | ~800ms |
| SongLyrics_400k | 400,000 | ~400ms |
| SongLyrics_200k | 200,000 | ~250ms |
| SongLyrics_50k | 50,000 | ~100ms |
| SongLyrics_30k | 30,000 | ~80ms |
| SongLyrics_20k | 20,000 | ~60ms |
| SongLyrics_15k | 15,000 | ~50ms |
| SongLyrics_12k | 12,000 | ~45ms |
| SongLyrics_10k | 10,000 | ~40ms |

**Parallel Time = Max(~800ms) ≈ 800ms + overhead**
**Multi-Collection Time = Depends on Weaviate's internal parallelization**

---

## 📝 Notes

1. **Query Reusability:** 
   - Queries are generated once and reused
   - No embedding API calls during tests

2. **Fair Comparison:**
   - Same search queries as multi-collection tests
   - Same result limits
   - Same test duration

3. **Resource Usage:**
   - Parallel tests may use more client-side resources
   - Monitor client CPU/memory during tests

4. **Network Overhead:**
   - 9 HTTP requests vs 1 has more overhead
   - But should be negligible compared to query execution time

---

## 🎯 Success Criteria

This approach is **successful** if:
- ✅ Parallel execution is ≥30% faster than multi-collection
- ✅ Error rates are comparable (≤1% difference)
- ✅ Throughput (RPS) is higher
- ✅ Resource usage is acceptable

This approach **needs optimization** if:
- ❌ Parallel is slower due to overhead
- ❌ High error rates (network issues)
- ❌ Client-side resource exhaustion

---

## 🤝 Contributing

To add more search types or limits:

```bash
# Generate additional queries
python generate_parallel_queries.py --search-types vector --limits 300

# Create new locustfile (copy existing and modify)
cp locustfile_vector.py locustfile_vector_300.py
# Edit to load queries_vector_300.json
```

---

**Happy Testing! 🚀**

