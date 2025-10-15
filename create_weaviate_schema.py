"""
Script to create Weaviate schema with proper tokenization and indexing configuration.
Run this before starting the main processing to ensure schema is set up correctly.
"""

import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Configure, Property, DataType
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_optimized_schema():
    """Create Weaviate schema with optimized tokenization and indexing"""
    
    try:
        # Parse URL to extract protocol, host, and port
        url = config.WEAVIATE_URL
        is_https = url.startswith("https://")
        url_without_protocol = url.replace("https://", "").replace("http://", "")
        
        # Split host and port
        if ":" in url_without_protocol:
            host, port_str = url_without_protocol.split(":", 1)
            port_str = port_str.split("/")[0]
            port = int(port_str)
        else:
            host = url_without_protocol.split("/")[0]
            port = 443 if is_https else 80
        
        # Check if authentication is needed
        use_auth = config.WEAVIATE_API_KEY and config.WEAVIATE_API_KEY != "your-weaviate-api-key"
        
        logger.info(f"Connecting to Weaviate at {host}:{port} (HTTPS: {is_https}, Auth: {use_auth})")
        
        # Connect to Weaviate
        if host in ["localhost", "127.0.0.1"]:
            client = weaviate.connect_to_local(
                host=host,
                port=port,
                grpc_port=port + 1,
                headers={"X-OpenAI-Api-Key": config.WEAVIATE_API_KEY} if use_auth else None,
                skip_init_checks=True
            )
        else:
            # Remote connection (custom URL)
            from weaviate.connect import ConnectionParams
            
            client = weaviate.WeaviateClient(
                connection_params=ConnectionParams.from_url(
                    url=config.WEAVIATE_URL,
                    grpc_port=port + 1
                ),
                auth_client_secret=weaviate.auth.AuthApiKey(config.WEAVIATE_API_KEY) if use_auth else None,
                skip_init_checks=True
            )
            client.connect()
        
        logger.info(f"Connected to Weaviate at {config.WEAVIATE_URL}")
        
        # Check if collection already exists
        if client.collections.exists(config.WEAVIATE_CLASS_NAME):
            logger.warning(f"Collection '{config.WEAVIATE_CLASS_NAME}' already exists!")
            response = input("Do you want to delete and recreate it? (yes/no): ")
            if response.lower() == 'yes':
                client.collections.delete(config.WEAVIATE_CLASS_NAME)
                logger.info(f"Deleted existing collection '{config.WEAVIATE_CLASS_NAME}'")
            else:
                logger.info("Keeping existing collection. Exiting.")
                client.close()
                return
        
        # Create collection with optimized configuration
        collection = client.collections.create(
            name=config.WEAVIATE_CLASS_NAME,
            description="Song lyrics with metadata and embeddings",
            
            # Sharding configuration
            sharding_config=Configure.sharding(
                virtual_per_physical=128,
                desired_count=3,  # 3 shards
                desired_virtual_count=128
            ),
            
            # Replication configuration
            replication_config=Configure.replication(
                factor=1  # Replication factor of 1
            ),
            
            # # Vectorizer configuration - we're providing our own vectors
            # vectorizer_config=None,
            
            # # Vector index configuration
            # vector_index_config=Configure.VectorIndex.hnsw(
            #     distance_metric=wvc.config.VectorDistances.COSINE,
            #     ef_construction=128,
            #     ef=64,
            #     max_connections=32
            # ),
            
            # # Inverted index configuration - disable WAND
            # inverted_index_config=Configure.inverted_index(
            #     bm25_b=0.75,
            #     bm25_k1=1.2,
            #     index_null_state=True,
            #     index_property_length=True,
            #     index_timestamps=True,
            #     # WAND disabled for more accurate BM25 scoring
            #     stopwords_preset=wvc.config.StopwordsPreset.EN
            # ),
            
            # Properties with specific tokenization
            properties=[
                # Searchable text fields with WORD tokenization
                Property(
                    name="title",
                    data_type=DataType.TEXT,
                    description="Song title",
                    index_searchable=True,
                    index_filterable=False,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                Property(
                    name="lyrics",
                    data_type=DataType.TEXT,
                    description="Song lyrics content",
                    index_searchable=True,
                    index_filterable=False,
                    tokenization=wvc.config.Tokenization.WORD,
                ),
                
                # Filterable fields with FIELD tokenization
                Property(
                    name="tag",
                    data_type=DataType.TEXT,
                    description="Genre/category tag",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="artist",
                    data_type=DataType.TEXT,
                    description="Artist name",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="features",
                    data_type=DataType.TEXT,
                    description="Featured artists",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="song_id",
                    data_type=DataType.TEXT,
                    description="Unique song identifier",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="language_cld3",
                    data_type=DataType.TEXT,
                    description="Language detected by CLD3",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="language_ft",
                    data_type=DataType.TEXT,
                    description="Language detected by FastText",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                Property(
                    name="language",
                    data_type=DataType.TEXT,
                    description="Primary language",
                    index_searchable=False,
                    index_filterable=True,
                    tokenization=wvc.config.Tokenization.FIELD,
                ),
                
                # Numeric fields (automatically filterable)
                Property(
                    name="year",
                    data_type=DataType.INT,
                    description="Release year",
                    index_filterable=True,
                ),
                Property(
                    name="views",
                    data_type=DataType.INT,
                    description="Number of views",
                    index_filterable=True,
                ),
            ]
        )
        
        logger.info("=" * 70)
        logger.info(f"✅ Successfully created collection: {config.WEAVIATE_CLASS_NAME}")
        logger.info("=" * 70)
        logger.info("\nConfiguration Summary:")
        logger.info(f"  - Sharding: 3 shards")
        logger.info(f"  - Replication: Factor of 1")
        logger.info(f"  - Vectorizer: None (external embeddings)")
        logger.info(f"  - Vector Index: HNSW with cosine distance")
        logger.info(f"  - WAND: Disabled (accurate BM25 scoring)")
        logger.info(f"\nSearchable Fields (word tokenization):")
        logger.info(f"  - title")
        logger.info(f"  - lyrics")
        logger.info(f"\nFilterable Fields (field tokenization):")
        logger.info(f"  - tag, artist, features, song_id")
        logger.info(f"  - language_cld3, language_ft, language")
        logger.info(f"  - year, views (numeric)")
        logger.info("=" * 70)
        
        # Close connection
        client.close()
        logger.info("\n✅ Schema creation complete! You can now run: python process_lyrics.py")
        
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure Weaviate is running")
        logger.error("2. Check WEAVIATE_URL in config.py")
        logger.error("3. Verify network connectivity")
        raise


if __name__ == "__main__":
    print("=" * 70)
    print("Weaviate Schema Creator")
    print("=" * 70)
    print(f"\nWeaviate URL: {config.WEAVIATE_URL}")
    print(f"Collection Name: {config.WEAVIATE_CLASS_NAME}")
    print("\nThis will create a new collection with optimized indexing.")
    print("=" * 70)
    
    create_optimized_schema()

