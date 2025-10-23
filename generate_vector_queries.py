"""
Generate pure vector search queries for Weaviate performance testing.
Uses nearVector (semantic search only, no BM25).
Pre-generates embeddings to avoid API calls during testing.
"""

import json
import sys
from openai_client import create_sync_openai_client
import config

# 30 diverse search queries
SEARCH_QUERIES = [
    "love and heartbreak",
    "summer party vibes",
    "feeling alone tonight",
    "dance all night long",
    "broken dreams and hope",
    "city lights at midnight",
    "memories of yesterday",
    "living life to fullest",
    "chasing dreams forever",
    "never give up fighting",
    "friendship and loyalty",
    "money power respect",
    "family comes first always",
    "trust nobody believe yourself",
    "hustle grind every day",
    "success and motivation",
    "romantic love story",
    "pain and suffering",
    "celebration and joy",
    "freedom and liberty",
    "hope for better tomorrow",
    "struggle and perseverance",
    "peace and tranquility",
    "anger and revenge",
    "happiness and laughter",
    "sadness and tears",
    "victory and triumph",
    "loss and defeat",
    "passion and desire",
    "fear and courage"
]

# All collections
COLLECTIONS = [
    "SongLyrics",
    "SongLyrics_400k",
    "SongLyrics_200k",
    "SongLyrics_50k",
    "SongLyrics_30k",
    "SongLyrics_20k",
    "SongLyrics_15k",
    "SongLyrics_12k",
    "SongLyrics_10k"
]


def get_embedding_for_query(query_text):
    """Get embedding vector for query"""
    try:
        client, model = create_sync_openai_client()
        response = client.embeddings.create(model=model, input=query_text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_vector_multi_collection_query(query_vector, limit):
    """Generate pure vector search query for ALL collections in single request"""
    vector_str = json.dumps(query_vector)
    
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_query = f"""
        {collection}(
          nearVector: {{
            vector: {vector_str}
          }}
          limit: {limit}
        ) {{
          title
          tag
          artist
          year
          views
          features
          lyrics
          song_id
          language_cld3
          language_ft
          language
          _additional {{
            distance
            certainty
          }}
        }}
        """
        collection_queries.append(collection_query)
    
    # Combine all collection queries
    all_collections = "\n        ".join(collection_queries)
    
    return f"""
    {{
      Get {{
        {all_collections}
      }}
    }}
    """


def generate_vector_query_files(limit):
    """Generate vector query files for specific limit"""
    
    print(f"\n📊 Generating embeddings for limit {limit}...")
    query_embeddings = {}
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/30] {query}...", end=' ', flush=True)
        emb = get_embedding_for_query(query)
        if emb:
            query_embeddings[query] = emb
            print("✓")
        else:
            print("❌")
            return False
    
    # Generate vector search query file
    vector_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "pure_vector",
            "limit": limit,
            "vector": query_embeddings[query_text],
            "graphql": generate_vector_multi_collection_query(
                query_embeddings[query_text], limit
            )
        }
        vector_queries.append(query_data)
    
    filename = f"queries_vector_{limit}.json"
    with open(filename, "w") as f:
        json.dump(vector_queries, f, indent=2)
    
    print(f"✅ {filename}")
    return True


def main():
    """Generate vector query files for all limits"""
    limits = [10, 50, 100, 150, 200]
    
    print("=" * 70)
    print("PURE VECTOR SEARCH QUERY GENERATOR")
    print("=" * 70)
    print(f"Search type: nearVector (pure semantic, no BM25)")
    print(f"Limits: {limits}")
    print(f"Collections: {len(COLLECTIONS)}")
    print(f"Queries: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    for limit in limits:
        print(f"\n🔄 Generating for limit {limit}...")
        if not generate_vector_query_files(limit):
            return 1
    
    print("\n" + "=" * 70)
    print(f"✅ Generated {len(limits)} vector query files")
    print("=" * 70)
    print("\nFiles created:")
    for limit in limits:
        print(f"  • queries_vector_{limit}.json")
    print("\n💡 These use nearVector (pure semantic search)")
    print("   No BM25, only vector similarity!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

