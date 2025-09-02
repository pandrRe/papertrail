#!/usr/bin/env python3
"""
Prepare Topics for Search

This script adds full-text search and semantic search capabilities to the topics table:
1. Creates full-text indexes on display_name and description
2. Adds an embedding column
3. Generates embeddings for semantic search

Usage:
    python prepare_topics_search.py [--db-path path/to/database.duckdb]
"""

import argparse
import sys
import os
from pathlib import Path
import duckdb
import time
from google import genai
from google.genai import types
import numpy as np
from typing import List


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def initialize_gemini_client() -> genai.Client:
    """Initialize Gemini client with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Please set it with your Google AI API key."
        )

    client = genai.Client(api_key=api_key)
    return client


def generate_gemini_embeddings(
    client: genai.Client, texts: List[str]
) -> List[List[float]]:
    """Generate normalized embeddings using Gemini API"""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY", output_dimensionality=768
        ),
    )

    # Normalize embeddings to unit vectors
    normalized_embeddings = []
    for embedding_obj in result.embeddings:
        embedding_values_np = np.array(embedding_obj.values)
        normed_embedding = embedding_values_np / np.linalg.norm(embedding_values_np)
        normalized_embeddings.append(normed_embedding.tolist())

    return normalized_embeddings


def initialize_extensions(conn: duckdb.DuckDBPyConnection) -> None:
    """Initialize FTS and VSS extensions"""
    print("🔧 Installing and loading extensions...")

    try:
        # Install and load FTS extension
        conn.execute("INSTALL fts")
        conn.execute("LOAD fts")
        print("  ✅ FTS extension loaded")

        # Install and load VSS extension
        conn.execute("INSTALL vss")
        conn.execute("LOAD vss")
        print("  ✅ VSS extension loaded")

    except Exception as e:
        print(f"  ❌ Error loading extensions: {e}")
        raise


def check_topics_table(conn: duckdb.DuckDBPyConnection) -> dict:
    """Check if topics table exists and get statistics"""
    print("📊 Checking topics table...")

    try:
        # Check if table exists
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'topics' AND table_schema = 'main'
        """).fetchone()

        if not result:
            print("  ❌ Topics table not found")
            return {"exists": False}

        # Get row count
        count_result = conn.execute("SELECT COUNT(*) FROM topics").fetchone()
        row_count = count_result[0] if count_result else 0

        # Check if embedding column exists
        columns_result = conn.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'topics' AND column_name = 'embedding'
        """).fetchone()

        has_embedding = columns_result is not None

        print(f"  📋 Topics table found with {row_count:,} rows")
        print(f"  🔍 Embedding column exists: {has_embedding}")

        return {"exists": True, "row_count": row_count, "has_embedding": has_embedding}

    except Exception as e:
        print(f"  ❌ Error checking topics table: {e}")
        raise


def add_embedding_column(
    conn: duckdb.DuckDBPyConnection, force_rebuild: bool = False
) -> None:
    """Add embedding column to topics table if it doesn't exist"""
    print("🏗️  Adding embedding column...")

    # Drop existing embedding column if forcing rebuild
    if force_rebuild:
        try:
            conn.execute("ALTER TABLE topics DROP COLUMN embedding")
            print("  🗑️  Dropped existing embedding column")
        except Exception as e:
            if "does not exist" not in str(e).lower():
                print(f"  ⚠️  Warning dropping embedding column: {e}")

    try:
        conn.execute("ALTER TABLE topics ADD COLUMN embedding FLOAT[768]")
        print("  ✅ Embedding column added")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("  ⏭️  Embedding column already exists")
        else:
            print(f"  ❌ Error adding embedding column: {e}")
            raise


def create_fts_index(
    conn: duckdb.DuckDBPyConnection, force_rebuild: bool = False
) -> None:
    """Create full-text search index on topics"""
    print("📇 Creating full-text search index...")

    try:
        # Check if index already exists
        if not force_rebuild:
            try:
                # Try to use the index - if it works, it exists
                conn.execute("""
                    SELECT fts_main_topics.match_bm25(id, 'test') 
                    FROM topics LIMIT 1
                """)
                print("  ⏭️  FTS index already exists (use --force to rebuild)")
                return
            except:
                # Index doesn't exist, continue to create it
                pass

        # Drop existing index if forcing rebuild
        if force_rebuild:
            try:
                conn.execute("PRAGMA drop_fts_index('topics')")
                print("  🗑️  Dropped existing FTS index")
            except:
                pass  # Index might not exist

        # Create combined search text and FTS index
        print("  🔨 Building FTS index (this may take a while)...")
        start_time = time.time()

        conn.execute("""
            PRAGMA create_fts_index(
                topics,
                id, 
                display_name,
                description,
                stemmer = 'porter',
                stopwords = 'english',
                ignore = '(\\.|[^a-zA-Z0-9])+',
                strip_accents = 1,
                lower = 1,
                overwrite = 1
            )
        """)

        duration = time.time() - start_time
        print(f"  ✅ FTS index created in {duration:.2f}s")

        # Test the index
        test_result = conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT fts_main_topics.match_bm25(id, 'machine learning') as score
                FROM topics 
                WHERE score > 0
                LIMIT 5
            )
        """).fetchone()

        print(f"  🧪 FTS index test: {test_result[0]} results for 'machine learning'")

    except Exception as e:
        print(f"  ❌ Error creating FTS index: {e}")
        raise


def format_topic_text(topic_data: dict) -> str:
    """Format topic data into text for embedding generation"""
    topic = topic_data.get("display_name", "")
    description = topic_data.get("description", "")

    # Handle subfield, field, domain which are nested structures
    subfield = ""
    field = ""
    domain = ""

    if topic_data.get("subfield"):
        subfield = (
            topic_data["subfield"].get("display_name", "")
            if isinstance(topic_data["subfield"], dict)
            else ""
        )

    if topic_data.get("field"):
        field = (
            topic_data["field"].get("display_name", "")
            if isinstance(topic_data["field"], dict)
            else ""
        )

    if topic_data.get("domain"):
        domain = (
            topic_data["domain"].get("display_name", "")
            if isinstance(topic_data["domain"], dict)
            else ""
        )

    # Format the text
    text = f"TOPIC: {topic}"
    if description:
        text += f". TOPIC DESCRIPTION: {description}"
    if subfield:
        text += f". subfield: {subfield}"
    if field:
        text += f", field: {field}"
    if domain:
        text += f", domain: {domain}"

    return text.strip()


def generate_embeddings(
    conn: duckdb.DuckDBPyConnection,
    batch_size: int = 100,
    force_regenerate: bool = False,
) -> None:
    """Generate embeddings for all topics"""
    print("🧠 Generating topic embeddings...")

    # Initialize Gemini client
    print("  📥 Initializing Gemini client...")
    client = initialize_gemini_client()
    print("  ✅ Gemini client initialized")

    # Check how many topics need embeddings
    if not force_regenerate:
        null_embeddings = conn.execute("""
            SELECT COUNT(*) FROM topics WHERE embedding IS NULL
        """).fetchone()[0]

        if null_embeddings == 0:
            print("  ⏭️  All topics already have embeddings (use --force to regenerate)")
            return
        else:
            print(f"  📊 {null_embeddings:,} topics need embeddings")
    else:
        print("  🔄 Regenerating all embeddings...")

    # Get total count for progress tracking
    total_count = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    num_batches = (total_count + batch_size - 1) // batch_size

    print(
        f"  📦 Processing {total_count:,} topics in {num_batches} batches of {batch_size}"
    )

    start_time = time.time()
    processed = 0

    # Process in batches
    for i in range(num_batches):
        batch_start = time.time()
        offset = i * batch_size

        print(f"    📦 Processing batch {i + 1}/{num_batches} (offset: {offset:,})")

        # Get topics data for this batch
        topics_data = conn.execute(f"""
            SELECT 
                id,
                display_name,
                description,
                subfield,
                field,
                domain
            FROM topics 
            ORDER BY id
            LIMIT {batch_size} OFFSET {offset}
        """).fetchall()

        if not topics_data:
            break

        # Format text for each topic
        topic_texts = []
        topic_ids = []

        for topic in topics_data:
            topic_dict = {
                "display_name": topic[1],
                "description": topic[2],
                "subfield": topic[3],
                "field": topic[4],
                "domain": topic[5],
            }

            formatted_text = format_topic_text(topic_dict)
            topic_texts.append(formatted_text)
            topic_ids.append(topic[0])

        # Generate embeddings and update database
        try:
            # Generate embeddings using Gemini
            embeddings = generate_gemini_embeddings(client, topic_texts)

            # Update each topic individually to avoid SQL injection issues
            for topic_id, embedding in zip(topic_ids, embeddings):
                conn.execute(
                    "UPDATE topics SET embedding = ? WHERE id = ?",
                    [embedding, topic_id],
                )

            processed += len(topics_data)
            batch_duration = time.time() - batch_start

            print(
                f"      ✅ Updated {len(topics_data)} topics in {batch_duration:.2f}s"
            )
            print(
                f"      📈 Progress: {processed:,}/{total_count:,} ({processed / total_count * 100:.1f}%)"
            )

        except Exception as e:
            print(f"      ❌ Error processing batch {i + 1}: {e}")
            continue

    total_duration = time.time() - start_time
    print(f"  ✅ Embedding generation completed in {total_duration:.2f}s")
    print(f"  📈 Rate: {processed / total_duration:.0f} topics/second")

    # Verify embeddings were created
    embedded_count = conn.execute("""
        SELECT COUNT(*) FROM topics WHERE embedding IS NOT NULL
    """).fetchone()[0]

    print(f"  📊 Final count: {embedded_count:,} topics with embeddings")


def test_search_functionality(conn: duckdb.DuckDBPyConnection) -> None:
    """Test both FTS and semantic search"""
    print("🧪 Testing search functionality...")

    test_query = "automated driving"

    try:
        # Test FTS
        print(f"  🔍 Testing FTS with query: '{test_query}'")
        fts_results = conn.execute(f"""
            SELECT 
                id,
                display_name,
                fts_main_topics.match_bm25(id, '{test_query}') as bm25_score
            FROM topics 
            WHERE bm25_score > 0
            ORDER BY bm25_score DESC
            LIMIT 10
        """).fetchall()

        print(f"    📊 FTS found {len(fts_results)} results")
        for result in fts_results[:10]:
            print(f"      - {result[1]} (score: {result[2]:.2f})")

        # Test semantic search
        print(f"  🧠 Testing semantic search with query: '{test_query}'")

        # Initialize Gemini client
        client = initialize_gemini_client()

        # Generate embedding for the test query
        query_embedding = generate_gemini_embeddings(client, [test_query])[0]

        semantic_results = conn.execute(
            """
            SELECT 
                id,
                display_name,
                array_cosine_similarity(embedding, ?::FLOAT[768]) as similarity_score
            FROM topics 
            WHERE embedding IS NOT NULL
            ORDER BY similarity_score DESC
            LIMIT 10
        """,
            [query_embedding],
        ).fetchall()

        print(f"    📊 Semantic search found {len(semantic_results)} results")
        for result in semantic_results[:10]:
            print(f"      - {result[1]} (similarity: {result[2]:.3f})")

        # Test hybrid search
        print(f"  🔀 Testing hybrid search with query: '{test_query}'")

        hybrid_results = conn.execute(
            f"""
            WITH fts AS (
                SELECT 
                    id,
                    display_name,
                    fts_main_topics.match_bm25(id, '{test_query}') as bm25_score
                FROM topics 
            ),
            semantic AS (
                SELECT 
                    id,
                    display_name,
                    array_cosine_similarity(embedding, ?::FLOAT[768]) as cosine_score
                FROM topics 
                WHERE embedding IS NOT NULL
            ),
            normalized_scores AS (
                SELECT 
                    COALESCE(fts.id, semantic.id) as id,
                    COALESCE(fts.display_name, semantic.display_name) as display_name,
                    COALESCE(fts.bm25_score, 0) as raw_bm25_score,
                    COALESCE(semantic.cosine_score, 0) as raw_cosine_score,
                    -- Min-max normalization for BM25 scores
                    CASE 
                        WHEN (SELECT MAX(bm25_score) FROM fts WHERE bm25_score > 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0) = 0 
                        THEN 0
                        ELSE (COALESCE(fts.bm25_score, 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0)) / 
                             NULLIF((SELECT MAX(bm25_score) FROM fts WHERE bm25_score > 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0), 0)
                    END as norm_bm25_score,
                    -- Cosine similarity is already normalized [0,1], but ensure it's positive
                    GREATEST(COALESCE(semantic.cosine_score, 0), 0) as norm_cosine_score
                FROM fts
                FULL OUTER JOIN semantic ON fts.id = semantic.id
            )
            SELECT 
                id,
                display_name,
                raw_bm25_score,
                raw_cosine_score,
                norm_bm25_score,
                norm_cosine_score,
                -- Convex combination: 0.1 * BM25 + 0.9 * cosine similarity
                (0.1 * norm_bm25_score + 0.9 * norm_cosine_score) AS hybrid_score
            FROM normalized_scores
            WHERE (raw_bm25_score > 0 OR raw_cosine_score > 0)
            ORDER BY hybrid_score DESC
            LIMIT 10
        """,
            [query_embedding],
        ).fetchall()

        print(f"    📊 Hybrid search found {len(hybrid_results)} results")
        for result in hybrid_results[:10]:
            print(
                f"      - {result[1]} (hybrid: {result[6]:.3f}, bm25: {result[4]:.3f}, cosine: {result[5]:.3f})"
            )

    except Exception as e:
        print(f"  ❌ Error testing search: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare topics table for search with FTS and embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Prepare topics with default settings
    python prepare_topics_search.py
    
    # Use specific database
    python prepare_topics_search.py --db-path /path/to/openalex.duckdb
    
    # Force rebuild of indexes and embeddings
    python prepare_topics_search.py --force
    
    # Use smaller batch size for embeddings
    python prepare_topics_search.py --batch-size 500
        """,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="openalex.duckdb",
        help="Path to the DuckDB database file (default: openalex.duckdb)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for embedding generation (default: 100)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild of FTS index and regenerate all embeddings",
    )

    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only test search functionality, do not create indexes or embeddings",
    )

    args = parser.parse_args()

    # Resolve database path
    db_path = Path(args.db_path).resolve()

    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        print("💡 Run setup_database.py and migrate_from_parquet.py first")
        sys.exit(1)

    print("DuckDB Topics Search Preparation")
    print("=" * 40)
    print(f"Database file: {db_path}")
    print(f"Database size: {db_path.stat().st_size:,} bytes")
    print(f"Batch size: {args.batch_size:,}")
    print(f"Force rebuild: {args.force}")

    # Connect to database
    try:
        conn = duckdb.connect(str(db_path))
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Initialize extensions
        initialize_extensions(conn)

        # Check topics table
        table_info = check_topics_table(conn)
        if not table_info["exists"]:
            print("❌ Topics table not found. Run migration first.")
            sys.exit(1)

        if args.test_only:
            test_search_functionality(conn)
        else:
            # Add embedding column if needed
            if not table_info["has_embedding"] or args.force:
                add_embedding_column(conn, force_rebuild=args.force)

            # Create FTS index
            create_fts_index(conn, force_rebuild=args.force)

            # Generate embeddings
            generate_embeddings(
                conn, batch_size=args.batch_size, force_regenerate=args.force
            )

            # Test functionality
            test_search_functionality(conn)

            print("\n🎉 Topics search preparation completed!")
            print("💡 You can now use both full-text and semantic search on topics")

    finally:
        conn.close()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    main()
