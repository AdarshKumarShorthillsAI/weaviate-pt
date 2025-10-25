# Performance Testing Suite

Load testing for Weaviate with automated query generation and reporting.

---

## 🎯 Purpose

Test search performance to:
- Identify bottlenecks
- Compare search strategies
- Measure response times across different result limits
- Establish baseline metrics for infrastructure decisions

---

## 📊 Test Scenarios

### Multi-Collection
Tests one GraphQL query searching 9 collections simultaneously.

### Single-Collection
Tests queries on SongLyrics (1M objects) only.

---

## 🔍 Search Types

| Type | Description | Use Case |
|------|-------------|----------|
| **BM25** | Keyword-only | Baseline, fastest |
| **Hybrid α=0.1** | 90% keyword, 10% vector | Keyword-focused |
| **Hybrid α=0.9** | 10% keyword, 90% vector | Semantic-focused |
| **Vector** | 100% semantic | Pure meaning |
| **Mixed** | Random combination | Realistic workload |

---

## 📏 Result Limits

Tests with: 10, 50, 100, 150, 200 results per collection

**Total:** 5 types × 5 limits × 2 scenarios = **50 tests**

---

## 🚀 Quick Start

### Quick Test (Verification)

```bash
./quick_test.sh
```

**Config:**
- Users: 2
- Duration: 20 seconds per test
- Total: 50 tests (~20 minutes)
- Purpose: Verify all scripts work

### Full Test (Benchmarking)

```bash
./run_all_pt_tests.sh
```

**Config:**
- Users: 100
- Duration: 5 minutes per test
- Ramp-up: 5 users/second
- Total: 50 tests (~4.5 hours)
- Purpose: Performance benchmarking

---

## 📂 File Structure

```
performance_testing/
├── README.md                      This file
├── QUICK_ACCESS.txt               Quick commands
├── HOW_TO_RUN_INDIVIDUAL_TESTS.md Examples
│
├── generate_all_queries.py        Query generator (cached!)
├── run_all_pt_tests.sh            Full test suite
├── quick_test.sh                  Quick test
│
├── multi_collection/              9 collections tests
│   ├── queries/                   Generated queries
│   ├── locustfile_*.py (5)        Test scripts
│   └── run_multi_collection_all_limits.sh
│
├── single_collection/             Single collection tests
│   ├── queries/                   Generated queries
│   ├── locustfile_*.py (5)        Test scripts
│   └── run_automated_tests.py
│
└── report_generators/             HTML report creators
    ├── generate_combined_report.py
    └── generate_single_report.py
```

---

## 🔧 Query Generation

### Generate All Queries

```bash
# Multi-collection (9 collections)
python generate_all_queries.py --type multi

# Single-collection (SongLyrics only)
python generate_all_queries.py --type single
```

**Features:**
- ✅ Embedding caching (saves 30 API calls!)
- ✅ Generates all 5 types × 5 limits = 25 files
- ✅ Saved to `queries/` subfolders
- ✅ First run: ~30 seconds, After: <1 second

### Generate Specific Types/Limits

```bash
# Only BM25
python generate_all_queries.py --type multi --search-types bm25

# Only limits 50 and 100
python generate_all_queries.py --type multi --limits 50 100

# BM25 + Vector, limits 10 and 200
python generate_all_queries.py --type multi --search-types bm25 vector --limits 10 200
```

---

## 📊 Test Parameters

**Full Test:**
- Users: 100 concurrent
- Ramp-up: 5 users/second
- Duration: 5 minutes per test
- No wait_time (maximum throughput)

**Quick Test:**
- Users: 2
- Duration: 20 seconds per test
- Same test coverage, faster

---

## 📈 Results

### Individual Reports

Saved to:
```
multi_collection_reports/
├── reports_10/
│   ├── bm25_report.html
│   ├── bm25_stats.csv
│   └── ... (5 search types)
├── reports_50/
└── ... (5 limit folders)
```

### Combined Reports

Generated in project root:
- `multi_collection_report.html` - All limits compared
- `single_collection_report.html` - All limits compared

**Generate reports:**
```bash
cd report_generators
python generate_combined_report.py
python generate_single_report.py
```

---

## 🎯 Running Individual Tests

See `HOW_TO_RUN_INDIVIDUAL_TESTS.md` for detailed examples.

**Quick example - BM25 only, limit 100:**

```bash
# Generate query
python generate_all_queries.py --type multi --search-types bm25 --limits 100

# Run test
cd multi_collection
locust -f locustfile_bm25.py --users 100 --run-time 5m --headless \
    --html ../../multi_collection_reports/reports_100/bm25_report.html \
    --csv ../../multi_collection_reports/reports_100/bm25
```

---

## 💡 Key Features

### Embedding Caching

**First run:**
```
Generating embeddings... (30 API calls, ~30 seconds)
Saved to embeddings_cache.json
```

**Subsequent runs:**
```
Loading cached embeddings... (0 API calls, <1 second)
```

**Savings:** 30 OpenAI API calls every run!

### Query Organization

Queries saved to dedicated folders:
```
multi_collection/queries/
├── queries_bm25_10.json
├── queries_bm25_50.json
└── ... (25 files total)
```

**Benefits:** Clean separation, easy management

### Consistent Locustfiles

All 10 locustfiles follow identical structure:
- All default to limit 200
- Runner scripts update for each limit
- No wait_time (maximum throughput)
- All use REST API (no gRPC)

---

## 📊 Sample Results

**Multi-Collection (9 collections, limit 200):**
```
Search Type    | Requests | Avg Time | RPS
---------------|----------|----------|-----
BM25           | 91,399   | 298ms    | 305
Hybrid 0.1     | 42,659   | 676ms    | 142
Vector         | 72,513   | 395ms    | 242
```

---

## ⚠️ Notes

- All locustfiles use REST API (Weaviate HTTP-only, no gRPC)
- No wait_time between requests (maximum load)
- Queries generated with cached embeddings (fast!)
- Results include HTML reports and CSV data

---

**Version:** 2.0  
**Last Updated:** 2025-10-25
