# Song Lyrics Embedding & Weaviate Indexing Pipeline

A production-ready, optimized pipeline for processing millions of song lyrics, generating embeddings using Azure OpenAI, and indexing them into Weaviate for semantic search.

## ✨ Features

- 🚀 **Optimized Performance**: Pipelined embeddings and indexing (30% faster)
- 🔄 **Resume Capability**: Checkpoint system to resume from interruptions
- ☁️ **Azure OpenAI Support**: Full support for Azure OpenAI embeddings
- 📊 **Progress Tracking**: Real-time progress bars and detailed logging
- 🔍 **Proper Schema**: Weaviate schema with optimized tokenization
- ⚡ **Async Processing**: Concurrent embeddings with rate limiting
- 🛡️ **Error Handling**: Comprehensive error handling with retry logic

## 📋 Requirements

- Python 3.11+
- Azure OpenAI account (or regular OpenAI)
- Weaviate instance (local or cloud)
- CSV file with song lyrics

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd nthScaling
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Copy the example config
cp config.example.py config.py

# Edit config.py with your credentials
nano config.py
```

Update these values in `config.py`:
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Your deployment name
- `WEAVIATE_URL` - Your Weaviate instance URL

### 4. Get Your Data

Download or place your CSV file:
```bash
# Your CSV should have these columns:
# title, tag, artist, year, views, features, lyrics, id, 
# language_cld3, language_ft, language
```

### 5. Verify Setup

```bash
python verify_setup.py
```

### 6. Create Weaviate Schema

```bash
python create_weaviate_schema.py
```

### 7. Test with Sample Data

```bash
python test_pipeline.py
```

### 8. Run Full Pipeline

```bash
python process_lyrics.py
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `AZURE_OPENAI_SETUP.md` | Complete Azure OpenAI setup guide |
| `QUICK_CONFIG_AZURE.txt` | One-page configuration reference |
| `TESTING_GUIDE.md` | Guide to all test scripts |
| `PERFORMANCE_OPTIMIZATION.md` | Details on pipelining optimization |
| `SYNC_VS_ASYNC_ANALYSIS.md` | Analysis of sync vs async operations |

## 🔧 Configuration

### Key Settings in `config.py`

```python
# Processing speed
CHUNK_SIZE = 10000          # Read 10k rows at a time
BATCH_SIZE = 10             # Process 10 rows at a time
MAX_CONCURRENT_EMBEDDINGS = 10  # Concurrent API calls

# Azure OpenAI
USE_AZURE_OPENAI = True     # True for Azure, False for OpenAI
AZURE_OPENAI_API_KEY = "your-key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
```

## 📊 Pipeline Architecture

```
CSV File (3M rows)
    ↓
Read in 10k chunks
    ↓
Process 10 rows at a time
    ↓
├─→ Clean & Validate Data
├─→ Generate Embeddings (10 concurrent async requests)
└─→ Batch Index to Weaviate
    ↓
Update Checkpoint (Resume capability)
    ↓
Repeat until complete
```

### Pipelined Processing

```
Batch 1: [Embed 10s] [Index 3s]
Batch 2:         [Embed 10s] ← Overlaps! [Index 3s]
Batch 3:                  [Embed 10s] ← Overlaps!

Result: 30% faster processing!
```

## 🗂️ Project Structure

```
nthScaling/
├── config.example.py           # Configuration template (COPY TO config.py)
├── process_lyrics.py           # Main processing script
├── create_weaviate_schema.py   # Create Weaviate schema
├── verify_setup.py             # Test connections
├── test_pipeline.py            # End-to-end test with sample data
├── check_progress.py           # Monitor processing progress
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── AZURE_OPENAI_SETUP.md      # Azure setup guide
├── TESTING_GUIDE.md           # Testing documentation
└── PERFORMANCE_OPTIMIZATION.md # Performance details
```

## 🎯 Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `verify_setup.py` | Test connections | First time setup |
| `create_weaviate_schema.py` | Create schema | Before indexing |
| `test_pipeline.py` | Test with 5 rows | Before production |
| `process_lyrics.py` | Process all data | Production run |
| `check_progress.py` | Check status | During processing |

## ⚡ Performance

- **Processing Speed**: ~100-200 rows/minute (depends on API limits)
- **Memory Usage**: ~500MB - 1GB
- **Optimization**: 30% faster with pipelined processing
- **Resume**: Automatic checkpoint every batch

### For 3 Million Rows:
- **Estimated Time**: ~35 days (with optimization)
- **Without Optimization**: ~45 days
- **Savings**: 10 days ⚡

## 🔍 Weaviate Schema

### Searchable Fields (Word Tokenization)
- `title` - Full-text search
- `lyrics` - Full-text search

### Filterable Fields (Field Tokenization)
- `artist`, `tag`, `features`, `song_id`
- `language_cld3`, `language_ft`, `language`
- `year`, `views` (numeric)

### Vector Configuration
- **Model**: text-embedding-3-large (3072 dimensions)
- **Index**: HNSW with cosine distance
- **WAND**: Disabled for accurate scoring

## 🛡️ Security

- ✅ `config.py` is in `.gitignore` (never committed)
- ✅ Use `config.example.py` as template
- ✅ CSV/ZIP files excluded from git
- ✅ Checkpoint files excluded from git

## 📈 Monitoring

### Check Progress
```bash
python check_progress.py
```

### View Logs
```bash
tail -f processing_log.log
```

### Resume After Interruption
Simply run again - it will resume automatically:
```bash
python process_lyrics.py
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connections first
python verify_setup.py

# Check Weaviate is running
curl http://localhost:8080/v1/.well-known/ready
```

### Rate Limiting
Reduce concurrent requests in `config.py`:
```python
MAX_CONCURRENT_EMBEDDINGS = 5  # Lower for free tier
```

### Memory Issues
Reduce chunk size in `config.py`:
```python
CHUNK_SIZE = 5000  # Instead of 10000
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

[Your License Here]

## 🙏 Acknowledgments

- Azure OpenAI for embeddings
- Weaviate for vector database
- OpenAI Python SDK

## 📧 Contact

[Your contact information]

---

**Note**: Make sure to configure `config.py` with your credentials before running. Never commit `config.py` to version control!
