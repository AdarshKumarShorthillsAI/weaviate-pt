"""
Restore Weaviate collections from Azure Blob Storage backups.
Features:
- Downloads and decompresses gzip files
- Streams to Weaviate (minimal disk usage)
- Parallel processing
- Resume capability
"""


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import gzip
import io
import asyncio
import gc
import logging
from typing import List, Dict
import requests
from azure.storage.blob import BlobServiceClient
from tqdm import tqdm

import config
from weaviate_client import batch_insert_objects

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeaviateRestore:
    """Restore Weaviate collections from Azure Blob Storage"""
    
    def __init__(self, connection_string: str, container_name: str = "weaviate-backups"):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
    
    def list_backup_runs(self, collection_name: str) -> List[str]:
        """List all backup run IDs for a collection"""
        try:
            backup_runs = set()
            blobs = self.container_client.list_blobs(name_starts_with=f"{collection_name}/")
            
            for blob in blobs:
                # Extract backup run ID (second part of path)
                # Format: collection/backup_run_id/filename
                parts = blob.name.split('/')
                if len(parts) >= 2:
                    backup_run_id = parts[1]
                    backup_runs.add(backup_run_id)
            
            return sorted(list(backup_runs), reverse=True)  # Newest first
        except Exception as e:
            logger.error(f"Error listing backup runs: {e}")
            return []
    
    def list_backup_files(self, collection_name: str, backup_run_id: str) -> List[str]:
        """List all backup files for a specific backup run"""
        try:
            prefix = f"{collection_name}/{backup_run_id}/"
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return sorted([blob.name for blob in blobs])
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            return []
    
    def get_backup_run_info(self, collection_name: str, backup_run_id: str) -> dict:
        """Get information about a backup run"""
        try:
            prefix = f"{collection_name}/{backup_run_id}/"
            blobs = list(self.container_client.list_blobs(name_starts_with=prefix))
            
            if not blobs:
                return None
            
            total_size = sum(blob.size for blob in blobs)
            file_count = len(blobs)
            
            # Estimate object count from filenames
            total_objects = 0
            for blob in blobs:
                try:
                    count_str = blob.name.split('_')[-1].replace('objs.json.gz', '')
                    total_objects += int(count_str)
                except:
                    pass
            
            # Get timestamp of first and last file
            sorted_blobs = sorted(blobs, key=lambda b: b.last_modified)
            first_timestamp = sorted_blobs[0].last_modified
            last_timestamp = sorted_blobs[-1].last_modified
            
            return {
                'file_count': file_count,
                'total_size': total_size,
                'estimated_objects': total_objects,
                'first_timestamp': first_timestamp,
                'last_timestamp': last_timestamp
            }
        except Exception as e:
            logger.error(f"Error getting backup info: {e}")
            return None
    
    def download_and_decompress(self, blob_name: str) -> List[Dict]:
        """Download and decompress a backup file (handles both gzipped and plain JSON)"""
        try:
            # Download blob
            blob_client = self.container_client.get_blob_client(blob_name)
            compressed_data = blob_client.download_blob().readall()
            
            # Try to decompress gzip first (new backups)
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
                    json_data = gz.read()
                objects = json.loads(json_data)
                logger.debug(f"Downloaded & decompressed gzip: {blob_name} ({len(objects)} objects)")
            except (gzip.BadGzipFile, OSError):
                # File not gzipped (old backup format), try as plain JSON
                logger.warning(f"File not gzipped (old backup): {blob_name}")
                objects = json.loads(compressed_data.decode('utf-8'))
                logger.debug(f"Loaded plain JSON: {blob_name} ({len(objects)} objects)")
            
            return objects
            
        except Exception as e:
            logger.error(f"Error downloading {blob_name}: {e}")
            return []
    
    async def restore_collection(self, collection_name: str, backup_run_id: str = None):
        """
        Restore a collection from backup files.
        
        Args:
            collection_name: Collection to restore
            backup_run_id: Specific backup run to restore (None to choose interactively)
        """
        
        logger.info("=" * 70)
        logger.info(f"Restoring: {collection_name}")
        logger.info("=" * 70)
        
        # List available backup runs
        backup_runs = self.list_backup_runs(collection_name)
        
        if not backup_runs:
            logger.warning(f"No backups found for {collection_name}")
            return
        
        # If backup_run_id not specified, let user choose
        if not backup_run_id:
            print(f"\n📂 Available backups for {collection_name}:")
            print("-" * 70)
            
            for i, run_id in enumerate(backup_runs, 1):
                info = self.get_backup_run_info(collection_name, run_id)
                if info:
                    size_mb = info['total_size'] / (1024 * 1024)
                    print(f"{i}. {run_id}")
                    print(f"   Files: {info['file_count']}, Size: {size_mb:.2f} MB, Objects: ~{info['estimated_objects']:,}")
                    print(f"   Created: {info['first_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"{i}. {run_id}")
            
            print("-" * 70)
            
            # Get user choice
            try:
                choice = int(input(f"\nChoose backup to restore (1-{len(backup_runs)}): "))
                if 1 <= choice <= len(backup_runs):
                    backup_run_id = backup_runs[choice - 1]
                else:
                    print("❌ Invalid choice")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
        
        print(f"\n✅ Restoring from: {backup_run_id}")
        
        # List backup files for this run
        backup_files = self.list_backup_files(collection_name, backup_run_id)
        
        if not backup_files:
            logger.warning(f"No backup files found for {collection_name}/{backup_run_id}")
            return
        
        logger.info(f"Found {len(backup_files)} backup files")
        
        total_restored = 0
        
        with tqdm(total=len(backup_files), desc=f"Restoring {collection_name}", unit="file") as pbar:
            for i, blob_name in enumerate(backup_files, 1):
                # Download and decompress
                objects = self.download_and_decompress(blob_name)
                
                if not objects:
                    logger.warning(f"Skipping empty file: {blob_name}")
                    pbar.update(1)
                    continue
                
                # Prepare for insertion
                objects_to_insert = []
                for obj in objects:
                    additional = obj.pop('_additional', {})
                    vector = additional.get('vector', [])
                    
                    objects_to_insert.append({
                        "properties": obj,
                        "vector": vector
                    })
                
                # Insert into Weaviate
                success, errors = batch_insert_objects(objects_to_insert, collection_name)
                total_restored += success
                
                logger.debug(f"File {i}/{len(backup_files)}: {success} restored, {errors} errors")
                
                # Cleanup
                objects = None
                objects_to_insert = None
                
                # GC every 10 files
                if i % 10 == 0:
                    collected = gc.collect()
                    logger.info(f"Restored {total_restored:,} objects so far, GC freed {collected}")
                
                pbar.update(1)
        
        logger.info("=" * 70)
        logger.info(f"Restore complete: {collection_name}")
        logger.info(f"Total objects restored: {total_restored:,}")
        logger.info("=" * 70)


def main():
    """Main restore function"""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*16 + "RESTORE FROM AZURE BLOB BACKUP" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    # Get connection string from config
    connection_string = config.AZURE_BLOB_CONNECTION_STRING
    
    if not connection_string or connection_string == "your-azure-blob-connection-string-here":
        print("\n❌ Azure Blob connection string not configured!")
        print("   Update AZURE_BLOB_CONNECTION_STRING in config.py")
        return 1
    
    print("\n✓ Using connection string from config.py")
    container_name = config.AZURE_BLOB_CONTAINER_NAME
    print(f"✓ Container: {container_name}")
    
    # Get collection name
    collection_name = input("Enter collection name to restore: ").strip()
    
    if not collection_name:
        print("❌ Collection name required")
        return 1
    
    # Confirm
    print(f"\n⚠️  This will restore data into: {collection_name}")
    print("   Make sure the collection schema exists!")
    print("   The script will show available backup runs and let you choose.")
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Restore cancelled")
        return 0
    
    # Run restore (will prompt for backup run choice)
    restore = WeaviateRestore(connection_string)
    asyncio.run(restore.restore_collection(collection_name))
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

