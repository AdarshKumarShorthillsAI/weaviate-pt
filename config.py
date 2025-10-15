"""
Configuration file for CSV processing and Weaviate indexing
Modify these values according to your setup

SETUP INSTRUCTIONS:
1. Copy this file to config.py: cp config.example.py config.py
2. Update config.py with your actual credentials
3. Never commit config.py to git (it's in .gitignore)
"""

# CSV Configuration
CSV_FILE_PATH = "song_lyrics.csv"
CHUNK_SIZE = 10000  # Read 10k rows at a time
BATCH_SIZE = 10     # Process 10 rows at a time

# OpenAI Configuration
# Set to True if using Azure OpenAI, False for regular OpenAI
USE_AZURE_OPENAI = True

# Azure OpenAI Configuration (if USE_AZURE_OPENAI = True)
AZURE_OPENAI_API_KEY = "your-azure-openai-api-key-here"
AZURE_OPENAI_ENDPOINT = "https://your-resource-name.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-02-01"  # API version
AZURE_OPENAI_DEPLOYMENT_NAME = "text-embedding-3-large"  # Your deployment name

# Regular OpenAI Configuration (if USE_AZURE_OPENAI = False)
OPENAI_API_KEY = "sk-your-openai-api-key-here"
OPENAI_MODEL = "text-embedding-3-large"

# Common OpenAI Settings
OPENAI_MAX_RETRIES = 3
OPENAI_TIMEOUT = 60

# Weaviate Configuration
WEAVIATE_URL = "http://localhost:8080"  # Replace with your Weaviate instance URL
WEAVIATE_API_KEY = "your-weaviate-api-key"  # Replace if authentication is enabled
WEAVIATE_CLASS_NAME = "SongLyrics"

# Processing Configuration
MAX_CONCURRENT_EMBEDDINGS = 10  # Number of concurrent embedding requests
CHECKPOINT_FILE = "processing_checkpoint.json"

# Logging Configuration
LOG_FILE = "processing_log.log"
LOG_LEVEL = "INFO"

# CSV Columns (metadata fields)
CSV_COLUMNS = [
    "title",
    "tag",
    "artist",
    "year",
    "views",
    "features",
    "lyrics",
    "id",
    "language_cld3",
    "language_ft",
    "language"
]

