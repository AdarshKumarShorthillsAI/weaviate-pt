# Weaviate Performance Testing & Optimization

Vector database performance testing and scaling project for song lyrics search.

---

## 🎯 Project Goals

1. Index 1M+ song lyrics with vector embeddings
2. Test search performance across different strategies
3. Find performance bottlenecks
4. Establish scaling strategies

---

## 🏗️ Infrastructure

**Weaviate Cluster:**
- Single node, single pod (current)
- Azure-hosted
- REST API only
- Version: 1.32.7

**Collections:**
- 9 collections (1M, 400k, 200k, 50k, 30k, 20k, 15k, 12k, 10k objects)
- Total: ~1.7M objects indexed
- Embeddings: 3072-dim (Azure OpenAI text-embedding-3-large)

---

## 📂 Project Structure

```
nthScaling/
├── indexing/                    Data processing & schema
├── backup_restore/              Azure Blob backup/restore
├── performance_testing/         Load testing suite
├── utilities/                   Helper scripts
├── config.py                    Configuration
└── requirements.txt             Dependencies
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Edit `config.py`:
```python
WEAVIATE_URL = "http://your-url:8080"
WEAVIATE_API_KEY = "your-key"
AZURE_OPENAI_API_KEY = "your-key"
AZURE_BLOB_CONNECTION_STRING = "your-connection-string"
```

### 3. Verify Setup

```bash
cd utilities
python verify_setup.py
```

### 4. Run Performance Tests

```bash
cd performance_testing
./quick_test.sh  # Quick (20 min)
# or
./run_all_pt_tests.sh  # Full (4.5 hours)
```

---

## 📊 Modules

### Indexing (`indexing/`)

**Purpose:** Data ingestion and schema management

**Main Scripts:**
- `create_weaviate_schema.py` - Create collection schema
- `process_lyrics.py` - Index data with embeddings
- `create_multiple_collections.py` - Create test collections
- `count_objects.py` - Count objects in collections

**Usage:**
```bash
cd indexing
python create_weaviate_schema.py
python process_lyrics.py
```

**See:** `indexing/README.md`

---

### Backup/Restore (`backup_restore/`)

**Purpose:** Azure Blob backup for quick restore

**Main Scripts:**
- `backup_v4.py` - Backup collections (REST API, 10k/batch)
- `restore_v4.py` - Restore with file range support
- `create_all_schemas.py` - Create schemas before restore
- `check_blob_backups.py` - List available backups

**Usage:**
```bash
cd backup_restore

# Backup
python backup_v4.py  # Select collection

# Restore
python restore_v4.py  # All files
python restore_v4.py --start 1 --end 10  # File range
```

**Why:** Restore in 1-2 hours vs 10-20 hours re-indexing

**See:** `backup_restore/README.md`

---

### Performance Testing (`performance_testing/`)

**Purpose:** Load testing and bottleneck identification

**Test Scenarios:**
- Multi-collection (9 collections in one query)
- Single-collection (1M objects)

**Search Types:**
- BM25 (keyword)
- Hybrid α=0.1 (keyword-focused)
- Hybrid α=0.9 (vector-focused)
- Vector (semantic)
- Mixed (realistic)

**Usage:**
```bash
cd performance_testing

# Quick test (50 tests, 20 seconds each)
./quick_test.sh

# Full test (50 tests, 5 minutes each)
./run_all_pt_tests.sh
```

**Output:**
- Individual reports: `*_collection_reports/reports_*/`
- Combined reports: `multi_collection_report.html`, `single_collection_report.html`

**See:** `performance_testing/README.md`

---

### Utilities (`utilities/`)

**Purpose:** Helper scripts and verification tools

**Main Scripts:**
- `verify_setup.py` - Verify all connections
- `count_objects.py` - Count objects
- `delete_collection.py` - Safe collection deletion
- `check_test_data.py` - Verify test results
- `analyze_lyrics_size.py` - Analyze data distribution

**Usage:**
```bash
cd utilities
python verify_setup.py
python count_objects.py
```

**See:** `utilities/README.md`

---

## 🔧 Configuration

**Main Settings (`config.py`):**

```python
# Weaviate
WEAVIATE_URL = "http://ip:port"
WEAVIATE_API_KEY = "your-key"
WEAVIATE_CLASS_NAME = "SongLyrics"

# Azure OpenAI
AZURE_OPENAI_API_KEY = "your-key"
AZURE_OPENAI_ENDPOINT = "https://your.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT = "text-embedding-3-large"

# Azure Blob
AZURE_BLOB_CONNECTION_STRING = "DefaultEndpointsProtocol=https;..."
AZURE_BLOB_CONTAINER_NAME = "weaviate-backups"
```

---

## 📈 Current Status

**Data:**
- ✅ 1M+ objects indexed
- ✅ 9 collection variants
- ✅ All backed up to Azure Blob

**Testing:**
- ✅ 50 tests completed
- ✅ All search types benchmarked
- ✅ Baseline metrics established

**Tools:**
- ✅ All scripts working
- ✅ Backup/restore optimized
- ✅ Memory-managed for large operations

---

## 🔮 Next Steps

1. **Async parallel search** - 9 collections searched simultaneously
2. **Pod scaling** - Test with 2x, 3x, 4x pods
3. **Node scaling** - Add nodes horizontally
4. **Combined scaling** - Optimal pod+node configuration

**Each step:**
- Backup → Change infra → Restore → Test → Compare

---

## 🆘 Common Issues

**"Cannot connect to Weaviate"**
→ Check WEAVIATE_URL in config.py

**"Azure Blob error"**
→ Check AZURE_BLOB_CONNECTION_STRING

**"0 objects restored"**
→ Check backup exists: `python check_blob_backups.py`

---
