# Utilities & Testing Scripts

Helper scripts for testing, verification, and analysis.

---

## 📂 Files

### Testing & Verification:
- **`verify_setup.py`** - Verify Weaviate setup and configuration
- **`test_graphql_query.py`** - Test GraphQL queries against Weaviate
- **`test_pipeline.py`** - Test complete indexing pipeline

### Analysis & Monitoring:
- **`analyze_errors.py`** - Analyze error logs from processing
- **`analyze_lyrics_size.py`** - Analyze lyrics data size/distribution
- **`check_all_collections.py`** - Check all Weaviate collections
- **`check_progress.py`** - Check processing progress
- **`check_test_data.py`** - Verify test data completeness

### Setup:
- **`setup_github.sh`** - GitHub repository setup script

---

## 🚀 Usage

### Test GraphQL Query:
```bash
python test_graphql_query.py
```

Tests sample queries to verify Weaviate is working.

### Verify Setup:
```bash
python verify_setup.py
```

Checks:
- Weaviate connection
- Schema exists
- Collections have data
- Configuration is valid

### Test Complete Pipeline:
```bash
python test_pipeline.py
```

Tests end-to-end data processing and indexing.

---

**Configuration:** Uses ../config.py  
**Dependencies:** See ../requirements.txt

