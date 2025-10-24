# Backup & Restore to Azure Blob Storage

This folder contains scripts for backing up and restoring Weaviate collections to/from Azure Blob Storage.

---

## 📂 Files

- **`backup_to_blob.py`** - Backup collections to Azure Blob Storage
- **`restore_from_blob.py`** - Restore collections from Azure Blob
- **`check_blob_backups.py`** - List and check existing backups
- **`test_backup_restore.py`** - Test backup/restore on small collection

---

## 🚀 Quick Start

### 1. Configure Azure Blob

Edit `../config.py`:
```python
AZURE_BLOB_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=..."
AZURE_BLOB_CONTAINER_NAME = "weaviate-backups"
BACKUP_BATCH_SIZE = 1000
BACKUP_MAX_PARALLEL = 5
```

### 2. Backup All Collections
```bash
python backup_to_blob.py
```

**Features:**
- Streams directly to blob (no local disk usage)
- Gzip compression
- Parallel uploads
- Versioned backups (timestamp-based)

**Output Structure:**
```
Azure Blob Container:
├── SongLyrics/
│   └── backup_20251024_120000/
│       ├── batch00001_1000objs.json.gz
│       ├── batch00002_1000objs.json.gz
│       └── ...
├── SongLyrics_400k/
│   └── backup_20251024_120000/
│       └── ...
```

### 3. List Available Backups
```bash
python check_blob_backups.py
```

Shows all backups organized by collection and timestamp.

### 4. Restore from Backup
```bash
python restore_from_blob.py
```

**Interactive prompts:**
1. Select collection to restore
2. Select backup version (by timestamp)
3. Confirm restoration

**Features:**
- Downloads and decompresses gzip files
- Batched uploads to Weaviate
- Progress tracking
- Validates data integrity

---

## 🔧 Usage Examples

### Backup Specific Collection:
```python
# Edit backup_to_blob.py, modify:
collections_to_backup = ['SongLyrics', 'SongLyrics_400k']
```

### Test Backup/Restore Workflow:
```bash
python test_backup_restore.py
```

Tests on small collection (SongLyrics_10k):
1. Backs up
2. Deletes collection
3. Restores
4. Validates

---

## 📊 Backup Features

### Optimization:
- ✅ Streaming (no local disk)
- ✅ Gzip compression (~80% reduction)
- ✅ Parallel uploads
- ✅ Batch processing (1000 objects)
- ✅ Memory efficient

### Versioning:
- ✅ Timestamp-based folders
- ✅ Multiple backups per collection
- ✅ Easy to restore specific version

### Safety:
- ✅ Validates before restore
- ✅ Progress tracking
- ✅ Error handling
- ✅ Resumable (can retry failed batches)

---

## ⚠️ Important Notes

### Connection String Format:
```
DefaultEndpointsProtocol=https;
AccountName=youraccount;
AccountKey=yourkey;
EndpointSuffix=core.windows.net
```

Get from: Azure Portal → Storage Account → Access Keys

### Backup Size:
- 1M objects ≈ 500MB compressed
- 10M objects ≈ 5GB compressed
- Plan storage accordingly

### Restore Time:
- 1M objects: ~10-15 minutes
- Depends on network speed and Weaviate capacity

---

## 🔄 Backup Strategy

### Recommended Schedule:
```bash
# Daily backup (cron job)
0 2 * * * cd /path/to/project/backup_restore && python backup_to_blob.py

# Weekly cleanup (keep last 4 weeks)
0 3 * * 0 python cleanup_old_backups.py --keep-weeks 4
```

### Before Major Changes:
```bash
# Backup before schema changes
python backup_to_blob.py

# Make changes
...

# If issues, restore
python restore_from_blob.py
```

---

## 📋 Workflow Examples

### Full Backup Workflow:
```bash
# 1. Check current state
python count_objects.py

# 2. Backup all collections
python backup_to_blob.py

# 3. Verify backup
python check_blob_backups.py

# 4. (Optional) Test restore
python test_backup_restore.py
```

### Disaster Recovery:
```bash
# 1. List available backups
python check_blob_backups.py

# 2. Choose and restore
python restore_from_blob.py

# 3. Verify restoration
python ../indexing/count_objects.py
```

---

## 🎯 Success Indicators

Good Backup:
- ✅ All collections backed up
- ✅ Batch files created successfully
- ✅ No upload errors
- ✅ Timestamp folder created

Good Restore:
- ✅ All batches downloaded
- ✅ All objects inserted
- ✅ Final count matches backup
- ✅ No errors during process

---

**Last Updated:** 2025-10-24  
**Dependencies:** azure-storage-blob>=12.19.0  
**Configuration:** See ../config.py

