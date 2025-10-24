"""
Generate vector queries for SINGLE collection testing (SongLyrics only).
For testing the collection with most objects (1M).
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


def get_embedding_for_query(query_text):
    """Get embedding for query"""
    try:
        client, model = create_sync_openai_client()
        response = client.embeddings.create(model=model, input=query_text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_single_vector_query(query_vector, limit, collection_name):
    """Generate vector query for SINGLE collection"""
    vector_str = json.dumps(query_vector)
    
    return f"""
    {{
      Get {{
        {collection_name}(
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
      }}
    }}
    """


def generate_single_vector_files(limit, collection_name):
    """Generate vector query files for single collection at specific limit"""
    
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
    
    # Generate vector queries for single collection
    vector_queries = []
    for query_text in SEARCH_QUERIES:
        query_data = {
            "query_text": query_text,
            "search_type": "pure_vector",
            "collection": collection_name,
            "limit": limit,
            "graphql": generate_single_vector_query(
                query_embeddings[query_text], limit, collection_name
            )
        }
        vector_queries.append(query_data)
    
    filename = f"queries_single_vector_{limit}.json"
    with open(filename, "w") as f:
        json.dump(vector_queries, f, indent=2)
    
    print(f"✅ {filename}")
    return True


def main():
    """Generate single collection vector query files for all limits"""
    limits = [10, 50, 100, 150, 200]
    collection_name = config.WEAVIATE_CLASS_NAME  # SongLyrics
    
    print("=" * 70)
    print("SINGLE COLLECTION VECTOR QUERY GENERATOR")
    print("=" * 70)
    print(f"Collection: {collection_name} (collection with most objects)")
    print(f"Search type: nearVector (pure semantic)")
    print(f"Limits: {limits}")
    print(f"Queries: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    for limit in limits:
        print(f"\n🔄 Generating for limit {limit}...")
        if not generate_single_vector_files(limit, collection_name):
            return 1
    
    print("\n" + "=" * 70)
    print(f"✅ Generated {len(limits)} single-collection vector query files")
    print("=" * 70)
    print("\nFiles created:")
    for limit in limits:
        print(f"  • queries_single_vector_{limit}.json")
    print("\n💡 These query ONLY SongLyrics (single collection)")
    print("   For testing collection with highest object count (1M)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

