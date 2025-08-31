#!/usr/bin/env python3
"""
Prepare Works for Search

This script adds full-text search and semantic search capabilities to the works table:
1. Creates full-text indexes on display_name
2. Creates a separate work_display_name_embeddings table with HNSW index
3. Generates embeddings for semantic search

Usage:
    python prepare_works_search.py [--db-path path/to/database.duckdb]
"""

import argparse
import sys
from pathlib import Path
import duckdb
import time
from sentence_transformers import SentenceTransformer
from typing import List


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


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


def check_works_table(conn: duckdb.DuckDBPyConnection) -> dict:
    """Check if works table exists and get statistics"""
    print("📊 Checking works table...")

    try:
        # Check if table exists
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'works' AND table_schema = 'main'
        """).fetchone()

        if not result:
            print("  ❌ Works table not found")
            return {"exists": False}

        # Get row count
        count_result = conn.execute("SELECT COUNT(*) FROM works").fetchone()
        row_count = count_result[0] if count_result else 0

        # Check if embeddings table exists
        embeddings_result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'work_display_name_embeddings' AND table_schema = 'main'
        """).fetchone()

        has_embeddings_table = embeddings_result is not None

        print(f"  📋 Works table found with {row_count:,} rows")
        print(f"  🔍 Embeddings table exists: {has_embeddings_table}")

        return {
            "exists": True,
            "row_count": row_count,
            "has_embeddings_table": has_embeddings_table,
        }

    except Exception as e:
        print(f"  ❌ Error checking works table: {e}")
        raise


def create_embeddings_table(
    conn: duckdb.DuckDBPyConnection,
    force_rebuild: bool = False,
    embedding_dim: int = 384,
) -> None:
    """Create work_display_name_embeddings table if it doesn't exist"""
    print("🏗️  Creating embeddings table...")

    try:
        if force_rebuild:
            # Drop existing table if forcing rebuild
            try:
                conn.execute("DROP TABLE IF EXISTS work_display_name_embeddings")
                print("  🗑️  Dropped existing embeddings table")
            except Exception:
                pass

        # Create the embeddings table with dynamic dimensions
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS work_display_name_embeddings (
                work_id VARCHAR PRIMARY KEY,
                embedding FLOAT[{embedding_dim}] NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print(f"  ✅ Embeddings table created (dimensions: {embedding_dim})")

        # Create index on work_id for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_embeddings_work_id 
            ON work_display_name_embeddings(work_id)
        """)
        print("  ✅ Work ID index created")

    except Exception as e:
        if "already exists" in str(e).lower():
            print("  ⏭️  Embeddings table already exists")
        else:
            print(f"  ❌ Error creating embeddings table: {e}")
            raise


def create_fts_index(
    conn: duckdb.DuckDBPyConnection, force_rebuild: bool = False
) -> None:
    """Create full-text search index on works display_name"""
    print("📇 Creating full-text search index...")

    try:
        # Check if index already exists
        if not force_rebuild:
            try:
                # Try to use the index - if it works, it exists
                conn.execute("""
                    SELECT fts_main_works.match_bm25(id, 'test') 
                    FROM works LIMIT 1
                """)
                print("  ⏭️  FTS index already exists (use --force to rebuild)")
                return
            except Exception:
                # Index doesn't exist, continue to create it
                pass

        # Drop existing index if forcing rebuild
        if force_rebuild:
            try:
                conn.execute("PRAGMA drop_fts_index('works')")
                print("  🗑️  Dropped existing FTS index")
            except Exception:
                pass  # Index might not exist

        # Create FTS index on display_name
        print("  🔨 Building FTS index (this may take a while)...")
        start_time = time.time()

        conn.execute("""
            PRAGMA create_fts_index(
                works,
                id, 
                display_name,
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
                SELECT fts_main_works.match_bm25(id, 'machine learning') as score
                FROM works 
                WHERE score > 0
                LIMIT 5
            )
        """).fetchone()

        print(f"  🧪 FTS index test: {test_result[0]} results for 'machine learning'")

    except Exception as e:
        print(f"  ❌ Error creating FTS index: {e}")
        raise


def format_work_text(display_name: str) -> str:
    """Format work display_name for embedding generation"""
    if not display_name:
        return ""

    # Simple formatting - just use the display name as is
    # Could be enhanced to include title variations or other metadata
    return f"WORK: {display_name.strip()}"


def generate_embeddings(
    conn: duckdb.DuckDBPyConnection,
    batch_size: int = 10_000,
    force_regenerate: bool = False,
    model_name: str = "all-MiniLM-L6-v2",
) -> None:
    """Generate embeddings for all works and store in separate table"""
    print("🧠 Generating work embeddings...")

    # Initialize sentence transformer model
    print(f"  📥 Loading SentenceTransformer model: {model_name}")
    model = SentenceTransformer(model_name, device="mps")
    print(f"  ✅ Model loaded ({model_name})")

    # Get model dimensions for validation
    model_dim = model.get_sentence_embedding_dimension()
    print(f"  📏 Model dimensions: {model_dim}")

    # Check how many works need embeddings
    if not force_regenerate:
        # Count works that don't have embeddings yet
        missing_embeddings = conn.execute("""
            SELECT COUNT(*) FROM works w
            WHERE NOT EXISTS (
                SELECT 1 FROM work_display_name_embeddings e 
                WHERE e.work_id = w.id
            )
        """).fetchone()[0]

        if missing_embeddings == 0:
            print("  ⏭️  All works already have embeddings (use --force to regenerate)")
            return
        else:
            print(f"  📊 {missing_embeddings:,} works need embeddings")
    else:
        print("  🔄 Regenerating all embeddings...")
        # Clear existing embeddings if regenerating
        conn.execute("DELETE FROM work_display_name_embeddings")

    # Register embedding function
    def get_text_embedding_list(text_list: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = model.encode(text_list, normalize_embeddings=True)
        return embeddings.tolist()

    conn.create_function(
        "get_text_embedding_list",
        get_text_embedding_list,
        return_type=f"FLOAT[{model_dim}][]",
    )

    # Get total count for progress tracking
    if force_regenerate:
        total_count = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        base_query = "SELECT id, display_name FROM works WHERE display_name IS NOT NULL"
    else:
        total_count = conn.execute("""
            SELECT COUNT(*) FROM works w
            WHERE w.display_name IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM work_display_name_embeddings e 
                    WHERE e.work_id = w.id
                )
        """).fetchone()[0]
        base_query = """
            SELECT w.id, w.display_name 
            FROM works w
            WHERE w.display_name IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM work_display_name_embeddings e 
                    WHERE e.work_id = w.id
                )
        """

    num_batches = (total_count + batch_size - 1) // batch_size

    print(
        f"  📦 Processing {total_count:,} works in {num_batches} batches of {batch_size}"
    )

    start_time = time.time()
    processed = 0

    # Process in batches
    for i in range(num_batches):
        batch_start = time.time()
        offset = i * batch_size

        print(f"    📦 Processing batch {i + 1}/{num_batches} (offset: {offset:,})")

        # Get works data for this batch
        works_data = conn.execute(f"""
            {base_query}
            ORDER BY id
            LIMIT {batch_size} OFFSET {offset}
        """).fetchall()

        if not works_data:
            break

        # Format text for each work and prepare for batch insert
        work_texts = []
        work_ids = []
        insert_values = []

        for work in works_data:
            work_id = work[0]
            display_name = work[1]

            formatted_text = format_work_text(display_name)
            work_texts.append(formatted_text)
            work_ids.append(work_id)

        # Generate embeddings and prepare batch insert
        try:
            # Generate embeddings first
            embeddings = get_text_embedding_list(work_texts)

            # Prepare batch insert values
            for work_id, embedding in zip(work_ids, embeddings):
                insert_values.append((work_id, embedding))

            # Batch insert into embeddings table
            conn.executemany(
                "INSERT OR REPLACE INTO work_display_name_embeddings (work_id, embedding) VALUES (?, ?)",
                insert_values,
            )

            processed += len(works_data)
            batch_duration = time.time() - batch_start

            print(f"      ✅ Updated {len(works_data)} works in {batch_duration:.2f}s")
            print(
                f"      📈 Progress: {processed:,}/{total_count:,} ({processed / total_count * 100:.1f}%)"
            )

        except Exception as e:
            print(f"      ❌ Error processing batch {i + 1}: {e}")
            continue

    total_duration = time.time() - start_time
    print(f"  ✅ Embedding generation completed in {total_duration:.2f}s")
    print(f"  📈 Rate: {processed / total_duration:.0f} works/second")

    # Verify embeddings were created
    embedded_count = conn.execute("""
        SELECT COUNT(*) FROM work_display_name_embeddings
    """).fetchone()[0]

    print(f"  📊 Final count: {embedded_count:,} works with embeddings")


def create_hnsw_index(conn: duckdb.DuckDBPyConnection) -> None:
    """Create HNSW index on embeddings table for fast similarity search"""
    print("🔗 Creating HNSW index...")

    try:
        # Always drop existing index to ensure it's fresh
        try:
            conn.execute("DROP INDEX IF EXISTS hnsw_work_embeddings")
            print("  🗑️  Dropped existing HNSW index")
        except Exception:
            pass  # Index might not exist

        # Create HNSW index
        print("  🔨 Building HNSW index (this may take a while)...")
        start_time = time.time()

        conn.execute("""
            CREATE INDEX hnsw_work_embeddings 
            ON work_display_name_embeddings 
            USING HNSW (embedding) 
            WITH (metric = 'cosine')
        """)

        duration = time.time() - start_time
        print(f"  ✅ HNSW index created in {duration:.2f}s")

        # Test the index
        embedding_count = conn.execute("""
            SELECT COUNT(*) FROM work_display_name_embeddings
        """).fetchone()[0]

        print(f"  🧪 HNSW index covers {embedding_count:,} embeddings")

    except Exception as e:
        print(f"  ❌ Error creating HNSW index: {e}")
        # This might fail if VSS extension doesn't support HNSW yet
        print("  💡 Note: HNSW might not be available in your DuckDB version")


def test_search_functionality(
    conn: duckdb.DuckDBPyConnection, model_name: str = "all-MiniLM-L6-v2"
) -> None:
    """Test both FTS and semantic search"""
    print("🧪 Testing search functionality...")

    test_query = "machine learning algorithms"

    try:
        # Test FTS
        print(f"  🔍 Testing FTS with query: '{test_query}'")
        fts_results = conn.execute(f"""
            SELECT 
                id,
                display_name,
                fts_main_works.match_bm25(id, '{test_query}') as bm25_score
            FROM works 
            WHERE bm25_score > 0
            ORDER BY bm25_score DESC
            LIMIT 5
        """).fetchall()

        print(f"    📊 FTS found {len(fts_results)} results")
        for result in fts_results:
            print(f"      - {result[1][:80]}... (score: {result[2]:.2f})")

        # Test semantic search
        print(f"  🧠 Testing semantic search with query: '{test_query}'")

        model = SentenceTransformer(model_name, device="mps")
        model_dim = model.get_sentence_embedding_dimension()

        # Register embedding function
        def get_text_embedding_list(text_list: List[str]) -> List[List[float]]:
            """Generate embeddings for a list of texts"""
            embeddings = model.encode(text_list, normalize_embeddings=True)
            return embeddings.tolist()

        conn.create_function(
            "get_text_embedding_list",
            get_text_embedding_list,
            return_type=f"FLOAT[{model_dim}][]",
        )

        semantic_results = conn.execute(f"""
            SELECT 
                w.id,
                w.display_name,
                array_cosine_similarity(
                    e.embedding,
                    get_text_embedding_list(['{test_query}'])[1]
                ) as similarity_score
            FROM works w
            JOIN work_display_name_embeddings e ON w.id = e.work_id
            ORDER BY similarity_score DESC
            LIMIT 5
        """).fetchall()

        print(f"    📊 Semantic search found {len(semantic_results)} results")
        for result in semantic_results:
            print(f"      - {result[1][:80]}... (similarity: {result[2]:.3f})")

        # Test hybrid search
        print(f"  🔀 Testing hybrid search with query: '{test_query}'")

        hybrid_results = conn.execute(f"""
            WITH fts AS (
                SELECT 
                    id,
                    display_name,
                    fts_main_works.match_bm25(id, '{test_query}') as bm25_score
                FROM works 
            ),
            semantic AS (
                SELECT 
                    w.id,
                    w.display_name,
                    array_cosine_similarity(
                        e.embedding,
                        get_text_embedding_list(['{test_query}'])[1]
                    ) as cosine_score
                FROM works w
                JOIN work_display_name_embeddings e ON w.id = e.work_id
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
                -- Convex combination: 0.3 * BM25 + 0.7 * cosine similarity
                (0.3 * norm_bm25_score + 0.7 * norm_cosine_score) AS hybrid_score
            FROM normalized_scores
            WHERE (raw_bm25_score > 0 OR raw_cosine_score > 0)
            ORDER BY hybrid_score DESC
            LIMIT 5
        """).fetchall()

        print(f"    📊 Hybrid search found {len(hybrid_results)} results")
        for result in hybrid_results:
            print(
                f"      - {result[1][:60]}... (hybrid: {result[6]:.3f}, bm25: {result[4]:.3f}, cosine: {result[5]:.3f})"
            )

    except Exception as e:
        print(f"  ❌ Error testing search: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare works table for search with FTS and embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Prepare works with default settings
    python prepare_works_search.py
    
    # Use faster/smaller model for paper titles
    python prepare_works_search.py --model paraphrase-TinyBERT-L6-v2
    
    # Use specific database
    python prepare_works_search.py --db-path /path/to/openalex.duckdb
    
    # Force rebuild of indexes and embeddings
    python prepare_works_search.py --force
    
    # Use smaller batch size for embeddings
    python prepare_works_search.py --batch-size 500
    
    # Skip HNSW index if not supported
    python prepare_works_search.py --skip-hnsw
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
        default=10_000,
        help="Batch size for embedding generation (default: 1000)",
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

    parser.add_argument(
        "--skip-hnsw",
        action="store_true",
        help="Skip creating HNSW index (useful if not supported)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="paraphrase-MiniLM-L6-v2",
        help="""SentenceTransformer model name. Fast options for paper titles:
        - all-MiniLM-L12-v2 (384 dim, good quality/speed balance)
        - all-MiniLM-L6-v2 (384 dim, faster, default)
        - paraphrase-TinyBERT-L6-v2 (768 dim, smaller/faster)
        - all-distilroberta-v1 (768 dim, good for scientific text)
        - sentence-t5-base (768 dim, good semantic understanding)
        (default: all-MiniLM-L6-v2)""",
    )

    args = parser.parse_args()

    # Resolve database path
    db_path = Path(args.db_path).resolve()

    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        print("💡 Run setup_database.py and migrate_works.py first")
        sys.exit(1)

    print("🚀 DuckDB Works Search Preparation")
    print("=" * 40)
    print(f"📁 Database file: {db_path}")
    print(f"📊 Database size: {db_path.stat().st_size:,} bytes")
    print(f"📦 Batch size: {args.batch_size:,}")
    print(f"🔄 Force rebuild: {args.force}")
    print(f"🔗 Skip HNSW: {args.skip_hnsw}")
    print(f"🧠 Model: {args.model}")

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

        # Check works table
        table_info = check_works_table(conn)
        if not table_info["exists"]:
            print("❌ Works table not found. Run migration first.")
            sys.exit(1)

        if args.test_only:
            test_search_functionality(conn, model_name=args.model)
        else:
            # Get model dimensions for table creation
            temp_model = SentenceTransformer(args.model, device="mps")
            model_dim = temp_model.get_sentence_embedding_dimension()
            print(f"📏 Using model with {model_dim} dimensions")

            # Create embeddings table
            create_embeddings_table(
                conn, force_rebuild=args.force, embedding_dim=model_dim
            )

            # Create FTS index
            create_fts_index(conn, force_rebuild=args.force)

            # Generate embeddings
            generate_embeddings(
                conn,
                batch_size=args.batch_size,
                force_regenerate=args.force,
                model_name=args.model,
            )

            # Create HNSW index (if not skipped)
            if not args.skip_hnsw:
                create_hnsw_index(conn)

            # Test functionality
            test_search_functionality(conn, model_name=args.model)

            print("\n🎉 Works search preparation completed!")
            print("💡 You can now use both full-text and semantic search on works")

    finally:
        conn.close()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    main()
