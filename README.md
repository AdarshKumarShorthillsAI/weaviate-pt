# Weaviate Performance Testing & Management Suite

**Complete toolkit for Weaviate indexing, backup, and performance testing.**

## 📂 Project Structure

```
nthScaling/
│
├── README.md ⭐                     This file - Start here
├── HANDOVER_GUIDE.md ⭐             Complete handover guide
│
├── config.py                        Main configuration
├── openai_client.py                 OpenAI client wrapper
├── weaviate_client.py               Weaviate client wrapper
├── error_tracker.py                 Error tracking
├── resource_manager.py              Resource management
├── requirements.txt                 Python dependencies
│
├── indexing/                        Data indexing & schema
│   ├── README.md
│   └── [6 Python scripts]
│
├── backup_restore/                  Azure Blob backup
│   ├── README.md
│   └── [5 Python scripts]
│
├── performance_testing/             Performance testing suite
│   ├── README.md
│   ├── QUICK_ACCESS.txt
│   ├── generate_all_queries.py      ONE query generator
│   ├── run_all_pt_tests.sh          Master test runner
│   ├── multi_collection/            (6 files)
│   ├── single_collection/           (2 files)
│   └── report_generators/           (3 files)
│
├── utilities/                       Helper scripts
│   ├── README.md
│   └── [10 Python scripts]
│
└── Results/                         Generated
    ├── multi_collection_reports/
    ├── single_collection_reports/
    ├── tax_reports/
    └── *.html
```

---

## 🎯 What Each Module Does

### 1. Indexing (`indexing/`)
**Purpose:** Data ingestion and schema management

**Main Scripts:**
- `create_weaviate_schema.py` - Create Weaviate schema
- `process_lyrics.py` - Process and index data
- `count_objects.py` - Count objects in collections

**Usage:**
```bash
cd indexing
python create_weaviate_schema.py
python process_lyrics.py
```

**Documentation:** `indexing/README.md`

---

### 2. Backup/Restore (`backup_restore/`)
**Purpose:** Azure Blob Storage backup & disaster recovery

**Main Scripts:**
- `backup_to_blob.py` - Backup all collections
- `restore_from_blob.py` - Restore from backup
- `check_blob_backups.py` - List available backups

**Usage:**
```bash
cd backup_restore
python backup_to_blob.py
python check_blob_backups.py
```

**Features:**
- Streaming (no local disk)
- Gzip compression (~80% reduction)
- Versioned backups

**Documentation:** `backup_restore/README.md`

---

### 3. Performance Testing (`performance_testing/`)
**Purpose:** Comprehensive load testing suite

**3 Test Scenarios:**

**Quick Start:**
```bash
cd performance_testing
./run_all_pt_tests.sh
```
- Generates ALL query files automatically
- Runs Multi-Collection (25 tests, ~2h 15m)
- Runs Single-Collection (25 tests, ~2h 15m)
- Generates combined reports
- Total time: ~4.5 hours

**Individual Scenarios:**

**a) Multi-Collection Only** (9 collections)
```bash
python generate_all_queries.py --type multi
cd multi_collection && ./run_multi_collection_all_limits.sh
```

**b) Single-Collection Only** (1M objects)
```bash
python generate_all_queries.py --type single
cd single_collection && python run_automated_tests.py
```

**c) Specific Test Type** (e.g., BM25 only)
```bash
python generate_all_queries.py --type multi --search-types bm25
# See HOW_TO_RUN_INDIVIDUAL_TESTS.md for details
```

**Documentation:** `performance_testing/README.md` and `performance_testing/QUICK_ACCESS.txt`

---

### 4. Utilities (`utilities/`)
**Purpose:** Helper scripts for verification and analysis

**Main Scripts:**
- `verify_setup.py` - Verify configuration
- `check_all_collections.py` - Check all collections
- `analyze_errors.py` - Analyze error logs

**Usage:**
```bash
cd utilities
python verify_setup.py
python check_all_collections.py
```

**Documentation:** `utilities/README.md`

---

## 🔑 Configuration

Edit `config.py`:

```python
# Weaviate
WEAVIATE_URL = "http://your-url:8080"
WEAVIATE_API_KEY = "your-key"

# Azure OpenAI
AZURE_OPENAI_API_KEY = "your-key"
AZURE_OPENAI_ENDPOINT = "https://your.openai.azure.com/"

# Azure Blob Storage
AZURE_BLOB_CONNECTION_STRING = "DefaultEndpointsProtocol=https;..."
AZURE_BLOB_CONTAINER_NAME = "weaviate-backups"
```

---

## 📊 Complete Workflow

### Initial Setup:
```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
nano config.py

# 3. Create schema
cd indexing && python create_weaviate_schema.py

# 4. Index data
python process_lyrics.py
```

---

## 🆘 Troubleshooting

### Common Issues:

**"Cannot import config"**
→ Scripts auto-configure paths. Ensure config.py exists in root.

**"Weaviate connection failed"**
→ Check WEAVIATE_URL in config.py

**"Azure Blob upload failed"**
→ Verify AZURE_BLOB_CONNECTION_STRING

**"Query files not found"**
→ Scripts auto-generate. Requires Azure OpenAI credentials.

---

## 📚 Documentation

**Main Guides (Root):**
- `README.md` - This file (project overview)
- `HANDOVER_GUIDE.md` - Complete handover guide

**Module Guides:**
- `indexing/README.md` - Indexing module
- `backup_restore/README.md` - Backup module
- `performance_testing/README.md` - PT module
- `utilities/README.md` - Utilities module

**Quick References:**
- `performance_testing/QUICK_ACCESS.txt` - One-line PT commands

---

## 📈 Performance Testing Details

### Search Types:
- **BM25** - Keyword-only (fastest)
- **Hybrid α=0.1** - Keyword-focused
- **Hybrid α=0.9** - Vector-focused
- **Vector** - Pure semantic
- **Mixed** - Realistic workload

### Result Limits:
- 10, 50, 100, 150, 200 results per collection

### Test Parameters:
- 100 concurrent users
- 5 minutes per test
- Fully automated

---

## ⚠️ Important Notes

### Weaviate Pagination:
- Offset limit: ~100k objects
- Use cursor-based for larger collections
- `copy_collection.py` handles automatically

### Backup Strategy:
- Versioned by timestamp
- Compression ~80% reduction
- Streaming (no local disk)

### Performance Testing:
- All scripts fully automated
- Auto-generate queries if missing
- Results are reproducible

---

## ✅ Verification Checklist

Before running tests:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] config.py configured with credentials
- [ ] Weaviate is running and accessible
- [ ] Azure credentials set (if using backup)

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| **Verify Setup** | `cd utilities && python verify_setup.py` |
| **Create Schema** | `cd indexing && python create_weaviate_schema.py` |
| **Index Data** | `cd indexing && python process_lyrics.py` |
| **Backup** | `cd backup_restore && python backup_to_blob.py` |
| **PT Multi** | `cd performance_testing/multi_collection && ./run_multi_collection_all_limits.sh` |
| **PT Single** | `cd performance_testing/single_collection && python run_automated_tests.py` |
| **Reports** | `cd performance_testing/report_generators && python generate_combined_report.py` |

---

**Version:** 3.0  
**Last Updated:** 2025-10-24  

**Total:** 50+ scripts, 6 documentation files, fully automated, enterprise-ready.

