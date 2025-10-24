# Weaviate Performance Testing - Complete Handover Guide

**For:** Manager/Team Lead  
**Date:** 2025-10-24  
**Purpose:** Complete setup and usage guide for Weaviate performance testing

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What's Included](#whats-included)
3. [Quick Start - All Tests](#quick-start)
4. [Test Scenarios Explained](#test-scenarios)
5. [Expected Results](#expected-results)
6. [Troubleshooting](#troubleshooting)
7. [File Organization](#file-organization)
8. [Dependencies](#dependencies)

---

## Overview

This package contains **complete performance testing suite** for Weaviate with:
- ✅ **3 test scenarios** (Multi-collection, Single-collection, Tax queries)
- ✅ **5 search types** (BM25, Hybrid 0.1, 0.9, Vector, Mixed)
- ✅ **5 result limits** (10, 50, 100, 150, 200)
- ✅ **Fully automated** scripts (one command runs everything)
- ✅ **Complete documentation** (guides for all scenarios)
- ✅ **Professional reports** (HTML + CSV outputs)

**Total:** 70 automated tests ready to run!

---

## What's Included

### 1. Multi-Collection Testing (9 Collections)
**Purpose:** Test search performance across all 9 collections simultaneously

**Files:**
- `performance_testing/multi_collection/run_multi_collection_all_limits.sh` ⭐

**What it tests:**
- 9 Weaviate collections (SongLyrics variants: 1M, 400k, 200k, ... 1k objects)
- 5 search types × 5 limits = 25 tests
- Time: ~2 hours 15 minutes

**Results:**
- Folder: `multi_collection_reports/`
- Report: `combined_performance_report_2nd.html`

---

### 2. Single-Collection Testing (1M Objects)
**Purpose:** Deep dive into single collection performance (highest object count)

**Files:**
- `performance_testing/single_collection/run_automated_tests.py` ⭐

**What it tests:**
- SongLyrics collection only (1 million objects)
- 5 search types × 5 limits = 25 tests
- Time: ~2 hours 15 minutes

**Results:**
- Folder: `single_collection_reports/`
- Report: `single_collection_performance_report.html`

---

### 3. Tax Query Testing (Domain-Specific)
**Purpose:** Test with tax/compliance-related queries (real use case)

**Files:**
- `performance_testing/tax_queries/run_all_tax_tests.sh` ⭐

**What it tests:**
- 30 tax-related queries (GST, Income Tax, TDS, etc.)
- 4 search types × 5 limits = 20 tests
- Time: ~1 hour 45 minutes

**Results:**
- Folder: `tax_reports/`
- Report: `tax_query_performance_report.html`

---

## Quick Start

### Run ALL Three Scenarios:

```bash
# 1. Multi-Collection (Most comprehensive)
cd performance_testing/multi_collection
./run_multi_collection_all_limits.sh

# 2. Single-Collection (Focused on 1M collection)
cd ../single_collection
python run_automated_tests.py

# 3. Tax Queries (Domain-specific)
cd ../tax_queries
./run_all_tax_tests.sh

# 4. Generate All Reports
cd ../report_generators
python generate_combined_report.py
python generate_single_report.py
python generate_tax_report.py
```

**Total Time:** ~6 hours for all three scenarios

**Note:** All scripts auto-generate query files if missing - no manual setup needed!

---

## Test Scenarios Explained

### Search Types (5):

| Type | Description | Use Case |
|------|-------------|----------|
| **BM25** | Keyword-only search | Exact term matching, fastest |
| **Hybrid α=0.1** | 90% keyword, 10% semantic | Balanced, good for most cases |
| **Hybrid α=0.9** | 10% keyword, 90% semantic | Conceptual understanding |
| **Vector (nearVector)** | 100% semantic | Pure meaning-based search |
| **Mixed** | Random combination | Realistic user behavior |

### Result Limits (5):

| Limit | Use Case |
|-------|----------|
| **10** | Quick preview, mobile apps |
| **50** | Standard search results |
| **100** | Extended results |
| **150** | Comprehensive results |
| **200** | Maximum typical results |

### Test Parameters:
- **Users:** 100 concurrent users
- **Ramp-up:** 5 users/second (gradual load)
- **Duration:** 5 minutes per test
- **Queries:** 30 diverse queries per test

---

## Expected Results

### Good Performance Indicators:

**Response Times:**
- BM25: 100-300ms (fastest)
- Hybrid: 400-700ms (moderate)
- Vector: 150-400ms (fast to moderate)
- Failure Rate: 0%

**Throughput:**
- BM25: 300-700 RPS (highest)
- Hybrid: 150-200 RPS (moderate)
- Vector: 200-600 RPS (high)

**Growth Pattern:**
- Response time should INCREASE with limit (10 → 200)
- Content size should grow ~20x (10 → 200)
- Throughput should DECREASE with limit

### Warning Signs:

⚠️ **Check if you see:**
- Flat response times across limits (indicates bug)
- Failure rate > 1%
- Response time > 5 seconds
- Inconsistent results between runs

---

## File Organization

### Complete Structure:

```
nthScaling/
├── config.py                           Configuration
├── openai_client.py                    OpenAI integration
├── requirements.txt                    Dependencies
│
├── performance_testing/                All PT scripts
│   ├── MASTER_README.txt               Start here!
│   ├── QUICK_ACCESS.txt                Quick commands
│   ├── RUN_TESTS_HERE.txt              Detailed guide
│   ├── README.md                       Full documentation
│   │
│   ├── multi_collection/               9 collections testing
│   │   ├── run_multi_collection_all_limits.sh  ⭐ RUN THIS
│   │   └── [8 more files]
│   │
│   ├── single_collection/              1M collection testing
│   │   ├── run_automated_tests.py      ⭐ RUN THIS
│   │   └── [4 more files]
│   │
│   ├── tax_queries/                    Tax query testing
│   │   ├── run_all_tax_tests.sh        ⭐ RUN THIS
│   │   └── [2 more files]
│   │
│   ├── report_generators/              Report creation
│   │   └── [3 Python files]
│   │
│   └── docs/                           Full guides
│       └── [2 documentation files]
│
├── multi_collection_reports/           Results (auto-created)
├── single_collection_reports/                          Results (auto-created)
├── tax_reports/                        Results (auto-created)
│
└── *.html                              Final reports (root)
```

---

## Dependencies

### Required:

```bash
# Install all dependencies
pip install -r requirements.txt
```

**Key packages:**
- locust (performance testing)
- openai (embeddings)
- requests (HTTP)
- python-dotenv (config)

### Configuration:

Edit `config.py`:
```python
WEAVIATE_URL = "http://your-weaviate-url:8080"
WEAVIATE_API_KEY = "your-api-key"
AZURE_OPENAI_API_KEY = "your-openai-key"
AZURE_OPENAI_ENDPOINT = "https://your-endpoint.openai.azure.com/"
```

---

## Troubleshooting

### Issue: "Query files not found"
**Solution:** Scripts auto-generate them. If it fails:
```bash
# Check Azure OpenAI credentials in config.py
cat config.py | grep AZURE_OPENAI
```

### Issue: "Cannot connect to Weaviate"
**Solution:** Verify Weaviate is running:
```bash
curl http://your-weaviate-url:8080/v1/.well-known/ready
```

### Issue: "Import config failed"
**Solution:** Scripts auto-configure paths. Verify config.py exists in root:
```bash
ls -la config.py
```

### Issue: "Results look wrong (flat lines)"
**Solution:** This was fixed. Use the updated scripts in `performance_testing/`.

---

## Step-by-Step First Run

### For someone new to run tests:

**1. Verify Setup (5 minutes):**
```bash
# Check config
cat config.py

# Check dependencies
pip list | grep locust
pip list | grep openai

# If missing:
pip install -r requirements.txt
```

**2. Run Multi-Collection Test (2h 15m):**
```bash
cd performance_testing/multi_collection
./run_multi_collection_all_limits.sh

# Script will:
# - Check for query files
# - Generate if missing (~2 min, calls Azure OpenAI)
# - Run 25 tests (~2 hours)
# - Generate report automatically
```

**3. View Results:**
```bash
cd ../..
open combined_performance_report_2nd.html
```

**4. (Optional) Run Other Tests:**
```bash
# Single-collection
cd performance_testing/single_collection
python run_automated_tests.py

# Tax queries
cd ../tax_queries
./run_all_tax_tests.sh
```

---

## What Each Script Does

### Multi-Collection Script:
```bash
./performance_testing/multi_collection/run_multi_collection_all_limits.sh
```

**Automatic Steps:**
1. Checks if query files exist
2. Generates them if missing (calls Azure OpenAI 30 times)
3. For each limit (10, 50, 100, 150, 200):
   - Updates locustfile with correct query file
   - Runs BM25 test (5 min)
   - Runs Hybrid 0.1 test (5 min)
   - Runs Hybrid 0.9 test (5 min)
   - Runs Vector test (5 min)
   - Runs Mixed test (5 min)
4. Generates combined HTML report
5. Shows summary

**No manual intervention needed!**

### Single-Collection Script:
```bash
cd performance_testing/single_collection
python run_automated_tests.py
```

**Same process as multi-collection but for single collection only.**

### Tax Queries Script:
```bash
cd performance_testing/tax_queries
./run_all_tax_tests.sh
```

**Tests with 30 tax-related queries instead of music queries.**

---

## Report Interpretation

### Combined Reports Show:

**1. Response Time Table:**
- How fast each search type is
- How time increases with result limit
- Which is fastest for each limit

**2. Throughput Table:**
- Requests handled per second
- Higher is better
- Decreases as limit increases (expected)

**3. 95th Percentile:**
- Worst-case performance
- Should be < 2x average (good)
- Should be < 5x average (acceptable)

**4. Detailed Breakdown:**
- Full metrics per limit
- Min/Max response times
- Failure rates

**5. Key Insights:**
- Fastest search type per limit
- Performance trends
- Recommendations

### Good Results:
- ✅ Response time grows with limit
- ✅ Failure rate = 0%
- ✅ 95th percentile < 2x average
- ✅ Consistent throughput

### Warning Signs:
- ⚠️ Flat response times (doesn't grow)
- ⚠️ Failure rate > 1%
- ⚠️ 95th percentile > 5x average
- ⚠️ Timeouts or errors

---

## Test Configuration

### To Modify Test Parameters:

Edit the shell scripts:
```bash
# Change number of users
--users 100      # Default: 100

# Change duration
--run-time 5m    # Default: 5 minutes (can use 1m, 10m, etc.)

# Change ramp-up speed
--spawn-rate 5   # Default: 5 users/second
```

### To Modify Queries:

Edit the query generator scripts:
```python
# In generate_test_queries.py or similar
SEARCH_QUERIES = [
    "your query 1",
    "your query 2",
    # ... (30 queries recommended)
]
```

### To Modify Collections:

Edit `generate_test_queries.py`:
```python
COLLECTIONS = [
    'YourCollection1',
    'YourCollection2',
    # ... (your collections)
]
```

---

## Success Checklist

Before considering tests complete:

- [ ] All scripts ran without errors
- [ ] All 3 HTML reports generated
- [ ] Response times increase with limit (not flat)
- [ ] Content sizes grow proportionally
- [ ] Failure rate = 0% for all tests
- [ ] Throughput values look reasonable
- [ ] No timeout or connection errors
- [ ] Reports open in browser successfully

---

## Time Estimates

| Scenario | Duration | Tests |
|----------|----------|-------|
| Multi-Collection | 2h 15m | 25 tests |
| Single-Collection | 2h 15m | 25 tests |
| Tax Queries | 1h 45m | 20 tests |
| **All Three** | **~6 hours** | **70 tests** |

**Note:** Query generation adds ~2 minutes per scenario (first run only)

---

## Output Files

### After Running All Tests:

```
nthScaling/
├── combined_performance_report_2nd.html      Multi-collection
├── single_collection_performance_report.html Single-collection
├── tax_query_performance_report.html         Tax queries
│
├── multi_collection_reports/
│   ├── reports_10/ (5 HTML + 5 CSV files)
│   ├── reports_50/ (5 HTML + 5 CSV files)
│   ... (5 folders total)
│
├── single_collection_reports/
│   ├── reports_10/ (5 HTML + 5 CSV files)
│   ... (5 folders total)
│
└── tax_reports/
    ├── tax_reports_10/ (4 HTML + 4 CSV files)
    ... (5 folders total)
```

**Total:** 3 combined reports + 70 individual reports + 70 CSV files

---

## Common Questions

### Q: How long does it take?
**A:** Each scenario takes ~2 hours. All three scenarios: ~6 hours.

### Q: Do I need to generate query files manually?
**A:** No! Scripts auto-generate if missing. Just run the script.

### Q: What if I get errors?
**A:** Check:
1. Weaviate is running
2. config.py has correct credentials
3. Dependencies installed (pip install -r requirements.txt)

### Q: Can I run tests in parallel?
**A:** Yes, you can run all 3 scenarios simultaneously on different terminals if you have enough resources.

### Q: How do I know if results are valid?
**A:** Check:
- Response time increases with limit ✅
- Content size grows ~20x from limit 10→200 ✅
- Failure rate = 0% ✅
- No flat lines in graphs ✅

### Q: Can I customize the tests?
**A:** Yes! Edit the query generator scripts or test parameters in shell scripts.

---

## Contact & Support

### If Issues Arise:

1. **Read documentation:**
   - `performance_testing/MASTER_README.txt`
   - `performance_testing/README.md`
   - `performance_testing/docs/MULTI_COLLECTION_TESTING_GUIDE.md`

2. **Check logs:**
   - Locust outputs error messages to console
   - CSV files show failure counts

3. **Verify setup:**
   - Config.py credentials
   - Weaviate connection
   - Dependencies installed

---

## Quick Reference Card

### Run Multi-Collection Tests:
```bash
cd performance_testing/multi_collection
./run_multi_collection_all_limits.sh
```

### Run Single-Collection Tests:
```bash
cd performance_testing/single_collection
python run_automated_tests.py
```

### Run Tax Query Tests:
```bash
cd performance_testing/tax_queries
./run_all_tax_tests.sh
```

### Generate All Reports:
```bash
cd performance_testing/report_generators
python generate_combined_report.py
python generate_single_report.py
python generate_tax_report.py
```

### View Reports:
```bash
open combined_performance_report_2nd.html
open single_collection_performance_report.html
open tax_query_performance_report.html
```

---

## Important Notes

### 1. Automated Query Generation
All scripts check for query files and generate if missing using Azure OpenAI.
- Requires valid AZURE_OPENAI_API_KEY in config.py
- Generates 30 queries with embeddings
- Only runs once (files are reused)

### 2. Test Parameters
Default settings:
- 100 concurrent users
- 5 minute duration per test
- 5 users/second ramp-up
- Can be modified in shell scripts

### 3. Results Organization
- Scripts in: `performance_testing/`
- Results in: `multi_collection_reports/`, `single_collection_reports/`, `tax_reports/`
- Reports in: Root directory (*.html)

### 4. No Manual Updates Needed
All scripts:
- Auto-detect missing files
- Auto-generate query files
- Auto-update locustfiles
- Auto-generate reports
- Just run and wait!

---

## Validation Checklist

Before delivering results to stakeholders:

Performance:
- [ ] BM25 is fastest search type
- [ ] Response times increase with limit
- [ ] Vector search works (not flat)
- [ ] No failures in any test

Data Quality:
- [ ] Content size grows proportionally
- [ ] All 25/20 tests completed
- [ ] CSV files have data
- [ ] HTML reports render correctly

Reports:
- [ ] All tables show 5 columns (including Vector)
- [ ] Graphs show trends (not flat)
- [ ] Insights section has recommendations
- [ ] Numbers look reasonable

---

## Handover Confidence

### ✅ Everything is Ready:

**Scripts:**
- Fully automated (one command per scenario)
- Auto-generate missing files
- Error handling included
- Clear progress indicators

**Documentation:**
- Quick start guides
- Full documentation
- Troubleshooting included
- Clear explanations

**Results:**
- Professional HTML reports
- Detailed CSV data
- Visual charts
- Key insights

**Organization:**
- Categorized by scenario
- Clear folder structure
- Easy to navigate
- Professional layout

---

## Final Notes

This is a **production-ready performance testing suite**:
- ✅ Battle-tested on real Weaviate clusters
- ✅ Handles edge cases (missing files, errors)
- ✅ Comprehensive coverage (70 tests)
- ✅ Professional reports
- ✅ Complete documentation

**Your manager can run these tests confidently without you present.**

---

**Prepared By:** Development Team  
**Date:** 2025-10-24  
**Version:** 3.0  
**Status:** Production Ready ✅

