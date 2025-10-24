# Performance Testing Suite

Complete load testing for Weaviate with automated query generation and reporting.

---

## 🚀 Quick Start - Run Everything

### One Command for All Tests:

```bash
./run_all_pt_tests.sh
```

**What it does:**
1. Generates ALL query files automatically (~2 min)
2. Runs Multi-Collection tests (25 tests, ~2h 15m)
3. Runs Single-Collection tests (25 tests, ~2h 15m)
4. Generates combined reports
5. Total time: ~4.5 hours

**Output:**
- `../multi_collection_reports/` - Multi-collection results
- `../single_collection_reports/` - Single-collection results
- `../combined_performance_report_2nd.html` - Combined report
- `../single_collection_performance_report.html` - Single report

---

## 📋 Test Scenarios

### 1. Multi-Collection (9 Collections)
**Tests:** All 9 collections simultaneously

**Collections:**
- SongLyrics (1M objects)
- SongLyrics_400k, 200k, 100k, 50k, 25k, 10k, 5k, 1k

**Command:**
```bash
cd multi_collection
./run_multi_collection_all_limits.sh
```

### 2. Single-Collection (SongLyrics Only)
**Tests:** Only the largest collection (1M objects)

**Command:**
```bash
cd single_collection
python run_automated_tests.py
```

---

## 🔍 Search Types (5)

| Type | Description | Use Case |
|------|-------------|----------|
| **BM25** | Keyword-only | Exact term matching, fastest |
| **Hybrid α=0.1** | 90% keyword, 10% vector | Balanced, keyword-focused |
| **Hybrid α=0.9** | 10% keyword, 90% vector | Semantic understanding |
| **Vector** | 100% semantic | Pure meaning-based |
| **Mixed** | Random mix | Realistic workload |

---

## 📊 Result Limits (5)

Tests with: 10, 50, 100, 150, 200 results per collection

---

## 🛠️ Query Generation

### Generate All Queries:

```bash
# Multi-collection (9 collections)
python generate_all_queries.py --type multi

# Single-collection (SongLyrics only)
python generate_all_queries.py --type single
```

### Generate Specific Types:

```bash
# Only BM25
python generate_all_queries.py --type multi --search-types bm25

# Only Hybrid
python generate_all_queries.py --type multi --search-types hybrid_01 hybrid_09

# Only Vector
python generate_all_queries.py --type multi --search-types vector
```

### Generate Specific Limits:

```bash
# Only limits 50 and 100
python generate_all_queries.py --type multi --limits 50 100
```

---

## 🎯 Run Individual Tests

**See:** `HOW_TO_RUN_INDIVIDUAL_TESTS.md` for detailed examples

### Quick Example - BM25 at Limit 50:

```bash
# 1. Generate query
python generate_all_queries.py --type multi --search-types bm25 --limits 50

# 2. Run test
cd multi_collection
locust -f locustfile_bm25.py --users 100 --spawn-rate 5 --run-time 5m --headless \
    --html ../../multi_collection_reports/reports_50/bm25_report.html \
    --csv ../../multi_collection_reports/reports_50/bm25
```

---

## 📂 File Structure

```
performance_testing/
├── README.md                      This file
├── HOW_TO_RUN_INDIVIDUAL_TESTS.md Individual test guide
├── QUICK_ACCESS.txt               Quick commands
│
├── generate_all_queries.py        ⭐ Unified query generator
├── run_all_pt_tests.sh            ⭐ Master test runner
│
├── multi_collection/              Multi-collection tests
│   ├── run_multi_collection_all_limits.sh
│   └── locustfile_*.py (5 files)
│
├── single_collection/             Single-collection tests
│   ├── run_automated_tests.py
│   └── locustfile_single_vector.py
│
└── report_generators/             Report creation
    ├── generate_combined_report.py
    ├── generate_single_report.py
    └── generate_tax_report.py
```

---

## ⚙️ Test Parameters

Default settings:
- **Users:** 100 concurrent
- **Ramp-up:** 5 users/second
- **Duration:** 5 minutes per test
- **Queries:** 30 diverse queries

To modify, edit the shell scripts or pass parameters to Locust.

---

## 📊 Understanding Results

### CSV Files (`*_stats.csv`):
- Request count
- Average response time
- 95th percentile
- Min/Max times
- Requests/second (RPS)
- Failure rate

### HTML Reports (`*_report.html`):
- Response time graphs
- Throughput charts
- Percentile breakdown
- Request distribution

### Combined Reports:
- Compare all search types
- Compare all limits
- Performance trends
- Recommendations

---

## 🆘 Troubleshooting

### "Query files not found"
→ Run `python generate_all_queries.py --type multi`

### "Cannot connect to Weaviate"
→ Check `../config.py` for correct WEAVIATE_URL

### "Azure OpenAI error"
→ Check Azure OpenAI credentials in `../config.py`

---

## 📝 Tips

1. **Start simple:** Run one test type at one limit first
2. **Use limit 10** for quick validation
3. **Generate queries once:** Reuse for multiple test runs
4. **Run full suite** only for final reports
5. **Monitor resources:** 100 users = significant load

---

**For complete details:** See `HANDOVER_GUIDE.md` in project root
