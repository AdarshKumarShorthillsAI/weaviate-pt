"""
Backup Weaviate collections to Azure Blob Storage.
Updated to Weaviate v4 client - Based on proven working approach.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import gc
import time
from typing import List, Dict
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient

import config
from weaviate_client import create_weaviate_client


# All available collections
ALL_COLLECTIONS = [
    "SongLyrics",
    "SongLyrics_400k",
    "SongLyrics_200k",
    "SongLyrics_100k",
    "SongLyrics_50k",
    "SongLyrics_30k",
    "SongLyrics_25k",
    "SongLyrics_20k",
    "SongLyrics_15k",
    "SongLyrics_12k",
    "SongLyrics_10k",
    "SongLyrics_5k",
    "SongLyrics_1k"
]

# Default properties (fallback if schema fetch fails)
DEFAULT_PROPERTIES = ['title', 'tag', 'artist', 'year', 'views', 'features', 'lyrics', 
                      'song_id', 'language_cld3', 'language_ft', 'language']


def get_collection_properties(collection_name):
    """Get actual properties from collection schema"""
    try:
        import requests
        
        headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
        
        response = requests.get(
            f"{config.WEAVIATE_URL}/v1/schema/{collection_name}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            schema = response.json()
            properties = [prop['name'] for prop in schema.get('properties', [])]
            return properties
        else:
            # Fallback to default properties
            return DEFAULT_PROPERTIES
    except:
        return DEFAULT_PROPERTIES


def get_batch_with_cursor_rest(collection_name, batch_size, cursor=None, properties=None):
    """
    Fetch batch using REST API (more reliable, no gRPC needed).
    
    Args:
        collection_name: Collection to query
        batch_size: Number of objects to fetch
        cursor: UUID to start after (None for first batch)
        properties: List of properties to fetch (None to auto-detect)
    
    Returns:
        List of objects with properties and vectors
    """
    try:
        import requests
        
        # Get actual properties from schema if not provided
        if properties is None:
            properties = get_collection_properties(collection_name)
        
        headers = {"Content-Type": "application/json"}
        if config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key":
            headers["Authorization"] = f"Bearer {config.WEAVIATE_API_KEY}"
        
        # Build GraphQL query with cursor
        # For Weaviate, cursor goes in 'after' parameter
        query_params = f'limit: {batch_size}'
        if cursor:
            query_params += f', after: "{cursor}"'
        
        # Build property list
        property_fields = '\n              '.join(properties)
        
        query = f"""
        {{
          Get {{
            {collection_name}({query_params}) {{
              {property_fields}
              _additional {{
                id
                vector
              }}
            }}
          }}
        }}
        """
        
        response = requests.post(
            f"{config.WEAVIATE_URL}/v1/graphql",
            headers=headers,
            json={"query": query},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            objects = result.get("data", {}).get("Get", {}).get(collection_name, [])
            return objects
        else:
            print(f"GraphQL error: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"Error fetching batch: {e}")
        return []


def upload_to_azure(file_path, blob_name, azure_connection_string, container_name):
    """Upload file to Azure Blob Storage"""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   ✅ Uploaded: {blob_name} ({file_size:.2f} MB)")
        
        blob_service_client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return False


def backup_collection(collection_name, azure_connection_string, container_name, 
                      backup_prefix, batch_size=10000):
    """
    Backup a single collection to Azure Blob Storage using REST API.
    
    Args:
        collection_name: Collection to backup
        azure_connection_string: Azure connection string
        container_name: Azure container name
        backup_prefix: Prefix for blob names (e.g., "backup_20251025")
        batch_size: Objects per file
    """
    print(f"\n{'='*70}")
    print(f"Backing up: {collection_name}")
    print(f"Batch size: {batch_size} objects per file")
    
    # Get actual properties from schema
    properties = get_collection_properties(collection_name)
    print(f"Properties: {len(properties)} fields")
    print(f"{'='*70}\n")
    
    cursor = None
    file_index = 1
    total_objects = 0
    
    while True:
        try:
            # Fetch batch using REST API (no gRPC issues!)
            print(f"Fetching batch {file_index}...", end=' ', flush=True)
            batch = get_batch_with_cursor_rest(collection_name, batch_size, cursor, properties)
            
            if not batch or len(batch) == 0:
                print("No more objects")
                break
            
            print(f"Got {len(batch)} objects")
            
            # Save to local JSON file
            file_name = f"{collection_name}_{backup_prefix}_{file_index}.json"
            print(f"   Saving to {file_name}...", end=' ', flush=True)
            
            with open(file_name, 'w') as json_file:
                json.dump(batch, json_file)
            
            file_size = os.path.getsize(file_name) / (1024 * 1024)
            print(f"{file_size:.2f} MB")
            
            # Upload to Azure
            blob_name = f"{collection_name}/{backup_prefix}/{file_name}"
            upload_success = upload_to_azure(file_name, blob_name, azure_connection_string, container_name)
            
            # Delete local file
            if upload_success:
                os.remove(file_name)
                print(f"   ✅ Cleaned up local file")
            
            # Update cursor and counters
            cursor = batch[-1]["_additional"]["id"]
            total_objects += len(batch)
            file_index += 1
            
            # Memory cleanup
            gc.collect()
            time.sleep(1)  # Brief pause
            
        except Exception as e:
            print(f"\n❌ Error in batch {file_index}: {e}")
            # Continue to next batch
            continue
    
    print(f"\n{'='*70}")
    print(f"✅ Backup complete: {collection_name}")
    print(f"   Total objects: {total_objects:,}")
    print(f"   Total files: {file_index - 1}")
    print(f"{'='*70}\n")
    
    return total_objects


def main():
    """Main backup function"""
    
    print("╔" + "="*68 + "╗")
    print("║" + " "*18 + "WEAVIATE BACKUP TO AZURE BLOB" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # Check Azure configuration
    if not config.AZURE_BLOB_CONNECTION_STRING or \
       config.AZURE_BLOB_CONNECTION_STRING == "your-azure-blob-connection-string-here":
        print("❌ Azure Blob connection string not configured!")
        print("   Update AZURE_BLOB_CONNECTION_STRING in config.py")
        return 1
    
    print(f"Weaviate URL: {config.WEAVIATE_URL}")
    print(f"Azure Container: {config.AZURE_BLOB_CONTAINER_NAME}")
    print()
    
    # Show available collections
    print("Available collections:")
    for i, col in enumerate(ALL_COLLECTIONS, 1):
        print(f"  {i:2}. {col}")
    
    print("\nOptions:")
    print("  • Enter 'all' to backup all collections")
    print("  • Enter collection number (e.g., '11' for SongLyrics_10k)")
    print("  • Enter multiple numbers (e.g., '1 11')")
    print()
    
    choice = input("Your choice: ").strip().lower()
    
    # Parse selection
    if choice == 'all':
        collections = ALL_COLLECTIONS
        print(f"\n✅ Selected: All {len(collections)} collections")
    else:
        try:
            indices = [int(x) for x in choice.split()]
            collections = [ALL_COLLECTIONS[i-1] for i in indices if 1 <= i <= len(ALL_COLLECTIONS)]
            
            if not collections:
                print("❌ No valid collections selected")
                return 1
            
            print(f"\n✅ Selected {len(collections)} collection(s):")
            for col in collections:
                print(f"   • {col}")
        except:
            print("❌ Invalid input")
            return 1
    
    # Generate backup prefix
    from datetime import datetime
    backup_prefix = datetime.now().strftime('backup_%Y%m%d_%H%M%S')
    
    print(f"\nBackup ID: {backup_prefix}")
    print(f"Batch size: 10,000 objects per file")
    print()
    
    # Confirm
    confirm = input("Proceed with backup? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Backup cancelled")
        return 0
    
    # Backup each collection (using REST API, no client needed)
    total_backed_up = 0
    
    for collection in collections:
        count = backup_collection(
            collection, 
            config.AZURE_BLOB_CONNECTION_STRING,
            config.AZURE_BLOB_CONTAINER_NAME,
            backup_prefix,
            batch_size=10000
        )
        total_backed_up += count
    
    print("\n" + "="*70)
    print("✅ ALL BACKUPS COMPLETE!")
    print("="*70)
    print(f"Total collections: {len(collections)}")
    print(f"Total objects: {total_backed_up:,}")
    print(f"Backup ID: {backup_prefix}")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

