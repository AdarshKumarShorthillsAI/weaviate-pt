"""
Generate performance test queries using TAX-RELATED search terms.
Creates queries for all search types: BM25, Hybrid (0.1, 0.9), Mixed, and Vector.
"""

import json
import sys
from openai_client import create_sync_openai_client
import config

# 30 TAX-RELATED search queries
SEARCH_QUERIES = [
    "income tax deduction section 80C",
    "GST registration process",
    "capital gains tax on property sale",
    "TDS rate chart for financial year",
    "advance tax payment due dates",
    "section 194C contractor payments",
    "depreciation rates under income tax",
    "tax audit limit for businesses",
    "penalty for late filing ITR",
    "carry forward losses tax treatment",
    "foreign tax credit claim procedure",
    "transfer pricing documentation requirements",
    "MAT and AMT provisions",
    "section 115BAA tax rate option",
    "tax on dividend income",
    "presumptive taxation scheme",
    "tax holiday for startups",
    "indirect tax compliance calendar",
    "customs duty exemption notifications",
    "service tax reverse charge mechanism",
    "input tax credit eligibility",
    "tax assessment procedure",
    "appeal filing time limits",
    "withholding tax on royalty payments",
    "permanent establishment taxation",
    "double taxation avoidance agreement",
    "equalization levy on digital services",
    "tax implications of ESOP",
    "section 10 exemptions list",
    "residential status tax impact"
]

# All collections to search
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
    """Get embedding for query"""
    try:
        client, model = create_sync_openai_client()
        response = client.embeddings.create(model=model, input=query_text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_bm25_query(query_text, limit):
    """Generate BM25 multi-collection query"""
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_queries.append(f"""
        {collection}(
          bm25: {{query: "{query_text}", properties: ["title", "lyrics"]}}
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
          _additional {{ score }}
        }}
        """)
    
    all_collections = "\n        ".join(collection_queries)
    return f"{{\n      Get {{\n        {all_collections}\n      }}\n    }}"


def generate_hybrid_query(query_text, vector, alpha, limit):
    """Generate hybrid multi-collection query"""
    vector_str = json.dumps(vector)
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_queries.append(f"""
        {collection}(
          hybrid: {{
            query: "{query_text}"
            alpha: {alpha}
            vector: {vector_str}
            properties: ["title", "lyrics"]
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
          _additional {{ score }}
        }}
        """)
    
    all_collections = "\n        ".join(collection_queries)
    return f"{{\n      Get {{\n        {all_collections}\n      }}\n    }}"


def generate_vector_query(vector, limit):
    """Generate nearVector multi-collection query"""
    vector_str = json.dumps(vector)
    collection_queries = []
    
    for collection in COLLECTIONS:
        collection_queries.append(f"""
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
          _additional {{ distance, certainty }}
        }}
        """)
    
    all_collections = "\n        ".join(collection_queries)
    return f"{{\n      Get {{\n        {all_collections}\n      }}\n    }}"


def generate_all_tax_query_files(limit):
    """Generate all query types for tax searches at specific limit"""
    
    print(f"\n📊 Generating embeddings for tax queries (limit={limit})...")
    query_embeddings = {}
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/30] {query[:50]}...", end=' ', flush=True)
        emb = get_embedding_for_query(query)
        if emb:
            query_embeddings[query] = emb
            print("✓")
        else:
            print("❌")
            return False
    
    # File 1: BM25
    bm25_queries = []
    for query_text in SEARCH_QUERIES:
        bm25_queries.append({
            "query_text": query_text,
            "search_type": "bm25",
            "limit": limit,
            "graphql": generate_bm25_query(query_text, limit)
        })
    
    with open(f"queries_tax_bm25_{limit}.json", "w") as f:
        json.dump(bm25_queries, f, indent=2)
    print(f"✅ queries_tax_bm25_{limit}.json")
    
    # File 2: Hybrid 0.1
    hybrid_01_queries = []
    for query_text in SEARCH_QUERIES:
        hybrid_01_queries.append({
            "query_text": query_text,
            "search_type": "hybrid_0.1",
            "alpha": 0.1,
            "limit": limit,
            "graphql": generate_hybrid_query(query_text, query_embeddings[query_text], 0.1, limit)
        })
    
    with open(f"queries_tax_hybrid_01_{limit}.json", "w") as f:
        json.dump(hybrid_01_queries, f, indent=2)
    print(f"✅ queries_tax_hybrid_01_{limit}.json")
    
    # File 3: Hybrid 0.9
    hybrid_09_queries = []
    for query_text in SEARCH_QUERIES:
        hybrid_09_queries.append({
            "query_text": query_text,
            "search_type": "hybrid_0.9",
            "alpha": 0.9,
            "limit": limit,
            "graphql": generate_hybrid_query(query_text, query_embeddings[query_text], 0.9, limit)
        })
    
    with open(f"queries_tax_hybrid_09_{limit}.json", "w") as f:
        json.dump(hybrid_09_queries, f, indent=2)
    print(f"✅ queries_tax_hybrid_09_{limit}.json")
    
    # File 4: Pure Vector
    vector_queries = []
    for query_text in SEARCH_QUERIES:
        vector_queries.append({
            "query_text": query_text,
            "search_type": "pure_vector",
            "limit": limit,
            "graphql": generate_vector_query(query_embeddings[query_text], limit)
        })
    
    with open(f"queries_tax_vector_{limit}.json", "w") as f:
        json.dump(vector_queries, f, indent=2)
    print(f"✅ queries_tax_vector_{limit}.json")
    
    # File 5: Mixed
    mixed_queries = []
    for i, query_text in enumerate(SEARCH_QUERIES):
        if i < 10:  # BM25
            query_data = {
                "query_text": query_text,
                "search_type": "bm25",
                "limit": limit,
                "graphql": generate_bm25_query(query_text, limit)
            }
        elif i < 20:  # Hybrid 0.1
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.1",
                "alpha": 0.1,
                "limit": limit,
                "graphql": generate_hybrid_query(query_text, query_embeddings[query_text], 0.1, limit)
            }
        else:  # Hybrid 0.9
            query_data = {
                "query_text": query_text,
                "search_type": "hybrid_0.9",
                "alpha": 0.9,
                "limit": limit,
                "graphql": generate_hybrid_query(query_text, query_embeddings[query_text], 0.9, limit)
            }
        mixed_queries.append(query_data)
    
    with open(f"queries_tax_mixed_{limit}.json", "w") as f:
        json.dump(mixed_queries, f, indent=2)
    print(f"✅ queries_tax_mixed_{limit}.json")
    
    return True


def main():
    """Generate tax query files for all limits"""
    limits = [10, 50, 100, 150, 200]
    
    print("=" * 70)
    print("TAX QUERIES GENERATOR - ALL SEARCH TYPES")
    print("=" * 70)
    print(f"Query theme: Tax and compliance related")
    print(f"Limits: {limits}")
    print(f"Collections: {len(COLLECTIONS)}")
    print(f"Queries: {len(SEARCH_QUERIES)}")
    print(f"Search types: BM25, Hybrid 0.1, Hybrid 0.9, nearVector, Mixed")
    print("=" * 70)
    
    for limit in limits:
        print(f"\n🔄 Generating for limit {limit}...")
        if not generate_all_tax_query_files(limit):
            return 1
    
    print("\n" + "=" * 70)
    print(f"✅ Generated {len(limits) * 5} tax query files")
    print("=" * 70)
    print("\nFiles created (per limit):")
    print("  • queries_tax_bm25_{limit}.json")
    print("  • queries_tax_hybrid_01_{limit}.json")
    print("  • queries_tax_hybrid_09_{limit}.json")
    print("  • queries_tax_vector_{limit}.json")
    print("  • queries_tax_mixed_{limit}.json")
    print("\n💡 All queries use tax-related search terms")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

