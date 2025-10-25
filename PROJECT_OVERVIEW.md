# Weaviate Performance Testing & Scaling Project

**Complete Overview - Data to Deployment**

---

## 🎯 Project Purpose

**Objective:** Build and test a scalable Weaviate vector database system for song lyrics search.

**Goals:**
1. Index 1M+ song lyrics with embeddings
2. Test search performance across different strategies
3. Find performance bottlenecks and scaling limits
4. Establish baseline metrics for infrastructure decisions

---

## 🏗️ Infrastructure

### Server Details

**Weaviate Server:**
```
Host: ssh xyz@xx.xx.xxx.xxx
Password: abc@abc
Weaviate URL: http://xx.xxx.xx.xx 
```

**Current Setup:**
- Single node
- Single pod 
- Azure-hosted

---

## 📊 Complete Workflow

### Phase 1: Data Acquisition & Preparation

**Source:** Kaggle Dataset
```
Dataset: genius-song-lyrics-with-language-information
Size: 8.4 GB CSV
Records: 1M+ song lyrics
Fields: title, artist, lyrics, year, views, language, etc.
```

**File:** `song_lyrics.csv` (in project root)

---

### Phase 2: Data Indexing

**Step 1: Schema Creation**
```bash
cd indexing
python create_weaviate_schema.py
```

**Creates:**
- Collection: SongLyrics (and variants)
- 11 properties (title, lyrics, artist, year, etc.)
- Vector index (cosine distance)
- BM25 configuration
- Sharding: 3 shards, Replication: 1
- No chunking (lyrics truncated if > 32k chars)

**Step 2: Data Processing & Indexing**
```bash
python process_lyrics.py
```

**What happens:**
1. Reads CSV in chunks (10k rows at a time)
2. Generates embeddings via Azure OpenAI (3072-dim)
3. Batch inserts to Weaviate (1000 objects/batch)
4. Resumes on failure (checkpoint-based)
5. Memory-optimized (GC after each chunk)


**Step 3: Create Collection Variants**
```bash
python create_multiple_collections.py
```

**Creates:**
- SongLyrics (1M objects)
- SongLyrics_400k, 200k, 50k, 30k, 20k, 15k, 12k, 10k
- Total: 9 collections for different scale testing

---

### Phase 3: Backup to Azure Blob

**Purpose:** Disaster recovery & quick restore after infrastructure changes

```bash
cd backup_restore
python backup_v4.py
```

**Backup Strategy:**
- Batch size: 10,000 objects per file
- Format: Plain JSON
- Storage: Azure Blob Storage
- Structure: `<collection>/backup_YYYYMMDD_HHMMSS/batch_*.json`

**Example:**
```
weaviate-backups/
├── SongLyrics/backup_20251025_120000/
│   ├── SongLyrics_backup_20251025_120000_1.json (10k objects)
│   ├── SongLyrics_backup_20251025_120000_2.json (10k objects)
│   └── ... (100 files for 1M objects)
```

**Why Backup?**
- Infrastructure changes require Weaviate restart
- Backup once, restore multiple times
- Test different configurations quickly
- No need to re-index (saves 10-20 hours!)

---

### Phase 4: Performance Testing

**Goal:** Find bottlenecks and optimal search strategy

**Test Scenarios:**

**A. Multi-Collection Search (9 collections simultaneously)**
- Tests searching across multiple collections in one query
- Simulates production workload

**B. Single-Collection Search (SongLyrics 1M only)**
- Tests single collection at scale
- Isolates performance characteristics

**Search Types Tested:**
1. **BM25** - Keyword-only (baseline)
2. **Hybrid α=0.1** - Keyword-focused (90% keyword, 10% vector)
3. **Hybrid α=0.9** - Vector-focused (10% keyword, 90% vector)
4. **Vector (nearVector)** - Pure semantic search
5. **Mixed** - Combination (realistic workload)

**Result Limits:**
- 10, 50, 100, 150, 200 results per collection

**Total Tests:** 5 types × 5 limits × 2 scenarios = **50 tests**

**Load:**
- Users: 100 concurrent
- Duration: 5 minutes per test

**Quick Test Available:**
```bash
cd performance_testing
./quick_test.sh  # 2 users, 20 seconds - For verification
```

---

## 🔍 Sample GraphQL Query

### Multi-Collection Search (All 9 collections in one query):

```graphql
{
  Get {
    SongLyrics(
      hybrid: {
        query: "love and heartbreak"
        alpha: 0.5
        vector: [0.123, 0.456, ..., 0.789]  # 3072-dim embedding
      }
      limit: 200
    ) {
      title
      artist
      lyrics
      year
      views
      _additional {
        score
        distance
      }
    }
    SongLyrics_400k(
      hybrid: { ... }
      limit: 200
    ) {
      title
      artist
      ...
    }
    # ... (7 more collections)
  }
}
```

**Returns:** Up to 1800 results (9 collections × 200 each)

---

## 📈 Project Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. DATA ACQUISITION                          │
│  Kaggle → song_lyrics.csv (8.4GB, 1M+ songs)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. DATA INDEXING                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ create_weaviate_schema.py                                │   │
│  │ Creates: SongLyrics collection                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ process_lyrics.py                                        │   │
│  │ • Read CSV chunks                                        │   │
│  │ • Generate embeddings (Azure OpenAI)                     │   │
│  │ • Batch insert to Weaviate                               │   │
│  │ Time: 10-20 hours                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ create_multiple_collections.py                           │   │
│  │ Creates: 12 collection variants (1M, 400k, ..., 1k)      │   │
│  │ Copy Data to other 8 collections for cost saving         │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3. BACKUP TO AZURE                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ backup_v4.py                                             │   │
│  │ • 10k objects per file                                   │   │
│  │ • Plain JSON format                                      │   │
│  │ • Azure Blob Storage                                     │   │
│  │ • Enables quick restore                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 4. PERFORMANCE TESTING                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Multi-Collection Tests (5 types × 5 limits)              │   │
│  │ • BM25, Hybrid 0.1, Hybrid 0.9, Vector, Mixed            │   │
│  │ • 100 users, 5 minutes each                              │   │
│  │ • Results → multi_collection_report.html                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Single-Collection Tests (5 types × 5 limits)             │   │
│  │ • Same search types                                      │   │
│  │ • Results → single_collection_report.html                │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 5. ANALYSIS & INSIGHTS                          │
│  • Compare search types (which is fastest?)                     │
│  • Compare result limits (optimal size?)                        │
│  • Identify bottlenecks                                         │
│  • Recommend infrastructure changes                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Next Steps (Future Roadmap)

### Step 1: Async Parallel Collection Search

**Current:**
- Single GraphQL query searches all 9 collections
- Weaviate processes sequentially
- Response time: ~270ms for 9 collections

**Proposed:**
- 9 separate async calls (one per collection)
- Process in parallel
- Expected: 4-5x faster (~50-60ms)

**Implementation:**
```python
import asyncio
import aiohttp

async def search_all_collections_parallel(query):
    tasks = []
    for collection in collections:
        task = search_single_collection(collection, query)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return combine_results(results)
```

**Test:** Compare against current single-query approach

---

### Step 2: Scale Pods (Same Node)

**Current:** X pods on single node

**Test:**
- Increase pods: 2x, 3x, 4x
- Same node configuration
- Measure: CPU utilization, throughput improvement

**Goal:** Find optimal pod count for single node

**After Change:**
1. Scale pods in Kubernetes
2. Restore from Azure Blob backup (quick!)
3. Run performance tests
4. Compare results

---

### Step 3: Scale Nodes (Horizontal Scaling)

**Current:** Single node

**Test:**
- Add nodes: 2, 3, 5 nodes
- Distribute pods across nodes
- Measure: Load distribution, throughput

**Goal:** Determine if horizontal scaling helps

---

### Step 4: Scale Pods Across Multiple Nodes

**Test:** Combination of more pods AND more nodes

**Matrix:**
- 2 nodes × 4 pods = 8 total pods
- 3 nodes × 3 pods = 9 total pods
- Find optimal configuration

---

## 🔄 Infrastructure Change Workflow

**Every time infrastructure changes:**

### Step 1: Backup (if data changes)
```bash
cd backup_restore
python backup_v4.py
# Select: all (or specific collections)
```

### Step 2: Change Infrastructure
- Modify Kubernetes config
- Scale pods/nodes
- Restart Weaviate

### Step 3: Create Schemas
```bash
cd backup_restore
python create_all_schemas.py
# Select: all
```

### Step 4: Restore Data
```bash
python restore_v4.py
# Can do parallel restore:
# Terminal 1: python restore_v4.py --start 1 --end 50
# Terminal 2: python restore_v4.py --start 51 --end 100
```

**Time:** ~1-2 hours for 1M objects (vs 10-20 hours to re-index!)

### Step 5: Run Performance Tests
```bash
cd performance_testing
./quick_test.sh  # Quick verification (20 min)
# Or
./run_all_pt_tests.sh  # Full test (4.5 hours)
```

### Step 6: Analyze Results
- Compare with previous configuration
- Check if performance improved
- Decide next scaling step

---

## 📊 Current Results & Metrics

### Collections Created:
```
SongLyrics:        1,000,416 objects ✅
SongLyrics_400k:     400,000 objects ✅
SongLyrics_200k:     200,000 objects ✅
SongLyrics_100k:     100,000 objects ✅
SongLyrics_50k:       50,000 objects ✅
... (13 collections total)
Total: ~1.7M objects indexed
```

### Performance Test Results:
```
Search Type      | Avg Response (Limit 200) | RPS
-----------------|--------------------------|-----
BM25             | 298ms                    | 305
Hybrid α=0.1     | 676ms                    | 142
Hybrid α=0.9     | 672ms                    | 143
Vector           | 395ms                    | 242
Mixed            | 554ms                    | 173
```

### Bottlenecks Identified:
- Hybrid searches slower than BM25 (vector computation overhead)
- Response time increases linearly with result limit
- Single-query multi-collection approach may be suboptimal

---

## 🛠️ Project Structure

```
nthScaling/
│
├── README.md                    Main project guide
├── PROJECT_OVERVIEW.md          This file - Complete overview
├── HANDOVER_GUIDE.md            For manager handover
├── GIT_SETUP_GUIDE.md           Git credential setup
│
├── config.py                    Central configuration
├── requirements.txt             Dependencies
├── [6 shared modules]           weaviate_client, openai_client, etc.
│
├── indexing/                    Data indexing & schema
│   ├── README.md
│   ├── create_weaviate_schema.py
│   ├── process_lyrics.py
│   ├── create_multiple_collections.py
│   └── count_objects.py
│
├── backup_restore/              Azure Blob backup/restore
│   ├── README.md
│   ├── backup_v4.py             Backup (10k/batch, REST API)
│   ├── restore_v4.py            Restore (fast, file range support)
│   ├── create_all_schemas.py   Schema creator
│   └── check_blob_backups.py   List backups
│
├── performance_testing/         Load testing suite
│   ├── README.md
│   ├── generate_all_queries.py  Query generator (cached embeddings!)
│   ├── run_all_pt_tests.sh      Master runner (50 tests)
│   ├── quick_test.sh            Quick test (20 min)
│   ├── multi_collection/        9 collections tests
│   ├── single_collection/       1M collection tests
│   └── report_generators/       HTML report creators
│
├── utilities/                   Helper scripts
│   ├── README.md
│   ├── verify_setup.py          Verify all connections
│   ├── count_objects.py         Count objects in collections
│   └── delete_collection.py     Safe collection deletion
│
└── Results/                     Generated reports
    ├── multi_collection_reports/
    ├── single_collection_reports/
    ├── multi_collection_report.html
    └── single_collection_report.html
```

---

## 📋 Key Technologies

**Vector Database:**
- Weaviate 1.24+ (v4 client)
- REST API
- Cosine similarity
- HNSW index

**Embeddings:**
- Azure OpenAI
- Model: text-embedding-3-large
- Dimensions: 3072
- Cost: ~$0.13 per 1M tokens

**Performance Testing:**
- Locust (load testing framework)
- 100 concurrent users
- GraphQL queries

**Storage:**
- Azure Blob Storage
- Backup/restore capability
- ~10k objects per file

---

## 🎯 Success Metrics

### Data Indexing:
- ✅ 1M+ objects indexed
- ✅ 13 collection variants created
- ✅ All with embeddings (3072-dim)

### Backup/Restore:
- ✅ Full backup to Azure Blob
- ✅ Restore tested and working
- ✅ Time: 1-2 hours vs 10-20 hours re-indexing

### Performance Testing:
- ✅ 50 comprehensive tests completed
- ✅ All search types benchmarked
- ✅ Results documented in HTML reports
- ✅ Baseline metrics established

---

## 🔮 Future Work

### 1. Async Parallel Collection Search

**Approach:**
```python
# Instead of:
single_query(all_9_collections)  # Sequential: ~270ms

# Do:
await asyncio.gather(
    query(collection1),
    query(collection2),
    ...
    query(collection9)
)  # Parallel: ~50-60ms expected
```

**Test Plan:**
- Implement parallel API
- Compare response times
- Measure CPU utilization
- Test with different user loads

**Expected:** 4-5x improvement

---

### 2. Pod Scaling (Same Node)

**Test Matrix:**
```
Config    | Pods | Expected Throughput | CPU Usage
----------|------|---------------------|----------
Current   | X    | Baseline            | Y%
Test 1    | 2X   | 1.5-2x              | 80-90%
Test 2    | 3X   | 2-2.5x              | 90-95%
Test 3    | 4X   | 2.5-3x or plateau   | 95-100%
```

**Workflow for Each Config:**
1. Backup current data
2. Scale pods in Kubernetes
3. Restart Weaviate
4. Create schemas: `python create_all_schemas.py`
5. Restore: `python restore_v4.py` (1-2 hours)
6. Test: `./run_all_pt_tests.sh` (4.5 hours)
7. Compare results
8. Find optimal pod count

---

### 3. Node Scaling (Horizontal)

**Test Matrix:**
```
Config    | Nodes | Pods/Node | Total Pods | Expected
----------|-------|-----------|------------|----------
Current   | 1     | X         | X          | Baseline
Test 1    | 2     | X         | 2X         | 1.8-2x
Test 2    | 3     | X         | 3X         | 2.5-3x
Test 3    | 5     | X         | 5X         | 4-5x or plateau
```

**Same workflow:** Backup → Change → Restore → Test → Compare

---

### 4. Combined Scaling (Pods + Nodes)

**Optimal Configuration Finding:**

**Test combinations:**
```
2 nodes × 4 pods = 8 total
3 nodes × 3 pods = 9 total
4 nodes × 2 pods = 8 total
5 nodes × 2 pods = 10 total
```

**Goal:** Find sweet spot for:
- Maximum throughput
- Best response time
- Cost efficiency
- Resource utilization

---

## 🔄 Why Backup/Restore is Critical

**Problem:**
- Infrastructure change = Weaviate restart
- Weaviate restart = Data lost
- Re-indexing = 10-20 hours per change
- Testing multiple configs = Days of re-indexing!

**Solution:**
- Backup once to Azure Blob (10k/file batches)
- Store all 1M objects in JSON files
- Restore in 1-2 hours (vs 10-20 hours!)
- Test multiple infrastructure configs quickly

**Value:**
- **Save time:** 1-2 hours vs 10-20 hours per config
- **Save cost:** No repeated OpenAI embedding calls
- **Enable rapid testing:** Test 5 configs in 1 day vs 1 week
- **Disaster recovery:** Quick recovery from any failure

---

## 📊 Testing Methodology

### Current Approach - Single Query:

```graphql
# One query searches all 9 collections
Get { 
  Collection1(...) { results }
  Collection2(...) { results }
  ...
  Collection9(...) { results }
}
```

**Pros:** Simple, one request  
**Cons:** Sequential processing, slower

---

### Future Approach - Parallel Queries:

```python
# 9 separate async queries
results = await asyncio.gather(
    search(Collection1),
    search(Collection2),
    ...
    search(Collection9)
)
```

**Pros:** Parallel, faster  
**Cons:** More complex, need API layer

---

## 💡 Key Insights

### From Testing:

1. **BM25 is fastest** (keyword-only, no vector overhead)
2. **Hybrid searches balance** speed and semantic understanding
3. **Vector search is fast** when properly configured
4. **Response time grows** with result limit (expected)
5. **Multiple collections** in one query may be bottleneck

### From Implementation:

1. **Backup/restore is essential** for rapid testing
2. **Batch size 10k** works well for backup
3. **REST API** more reliable than gRPC
4. **Memory management** critical for large operations
5. **Schema flexibility** needed (auto-detect properties)

---

## 📈 Expected Improvements

### From Async Parallel Search:
- Response time: 270ms → 50-60ms (4-5x faster) ✅
- Better CPU utilization
- Higher throughput

### From Pod Scaling:
- Linear improvement up to CPU limit
- 2x pods ≈ 1.5-2x throughput
- Diminishing returns after CPU saturation

### From Node Scaling:
- Near-linear scaling (distributed load)
- 2x nodes ≈ 1.8-2x throughput
- Better for large-scale workloads

### Combined:
- Potential: 10-20x improvement over current setup
- Depends on optimal configuration found through testing

---

## 🎓 Lessons Learned

### Data Indexing:
- Checkpoint-based resumption is essential
- Memory management prevents crashes
- Batch processing is key
- OpenAI rate limits are real constraint

### Backup/Restore:
- Simple is better (plain JSON vs complex streaming)
- REST API more reliable than client libraries
- Batch size matters (10k works, 5k safer)
- Always test on small collection first

### Performance Testing:
- Embedding caching saves massive time/cost
- Consistent test parameters essential
- Multiple scenarios reveal different characteristics
- Quick tests (2 users, 20s) validate, Full tests (100 users, 5min) benchmark

---

## 📝 Current Status

**Completed:**
- ✅ Data indexed (1M+ objects)
- ✅ Collection variants created (13 total)
- ✅ Backup system working
- ✅ Restore system working (fast!)
- ✅ Performance testing complete (50 tests)
- ✅ Baseline metrics established
- ✅ All tools documented

**Ready for:**
- ✅ Infrastructure scaling tests
- ✅ Parallel search implementation
- ✅ Manager handover

---

## 🎯 Recommendations

### For Your Manager:

1. **Review baseline metrics** in performance reports
2. **Understand backup/restore value** (saves 10-20 hours per test)
3. **Prioritize async parallel search** (biggest potential gain)
4. **Plan infrastructure tests** (pods, then nodes, then combined)

### For Implementation:

1. **Start with async parallel** (software change, no infra cost)
2. **Then test pod scaling** (same hardware, low risk)
3. **Then add nodes** (if pod scaling plateaus)
4. **Always backup before changes**
5. **Always run full PT after changes**

---

## 📖 Documentation Index

| Document | Purpose |
|----------|---------|
| **PROJECT_OVERVIEW.md** | This file - Complete project overview |
| **README.md** | Quick start & module navigation |
| **HANDOVER_GUIDE.md** | Manager handover guide |
| **GIT_SETUP_GUIDE.md** | Git credential setup |
| **indexing/README.md** | Indexing module guide |
| **backup_restore/README.md** | Backup/restore guide |
| **performance_testing/README.md** | PT comprehensive guide |
| **utilities/README.md** | Utilities guide |
| **performance_testing/QUICK_ACCESS.txt** | Quick PT commands |

---

## 🚀 Quick Command Reference

```bash
# Verify setup
cd utilities && python verify_setup.py

# Index data
cd ../indexing && python process_lyrics.py

# Backup all
cd ../backup_restore && python backup_v4.py  # Enter: all

# Restore with parallel
python restore_v4.py --start 1 --end 50  # Terminal 1
python restore_v4.py --start 51 --end 100  # Terminal 2

# Run quick PT test
cd ../performance_testing && ./quick_test.sh

# Run full PT suite
./run_all_pt_tests.sh
```

---

**Project Duration:** 2 weeks  
**Last Updated:** 2025-10-25  
**Version:** 1.0 - Production Ready  
**Status:** ✅ Complete & Ready for Scaling Tests

