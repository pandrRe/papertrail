#!/usr/bin/env python3
"""
Migrate OpenAlex Authors from Parquet Files to DuckDB

This script specifically handles the authors entity, extracting data from parquet files
and populating three tables:
1. authors - core author information (filtered by h-index >= 10)
2. author_topics - author-topic relationships from topic_share
3. author_affiliations - author-institution relationships from affiliations

Usage:
    python migrate_authors.py [--db-path path/to/database.duckdb] [--parquet-path path/to/parquet] [--min-h-index 10]
"""

import argparse
import sys
import tempfile
from pathlib import Path
import duckdb
import time
from typing import List

# Hardcoded parquet destination path (same as in other scripts)
parquet_destination_path = Path("/Volumes/T7/openalex-parquet")

# Default minimum h-index threshold for filtering
DEFAULT_MIN_H_INDEX = 4

# Chunking configuration
DEFAULT_CHUNK_SIZE = 80_000  # Number of records to process at once


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def get_author_parquet_files(parquet_path: Path) -> List[Path]:
    """Get all parquet files for authors entity"""
    authors_dir = parquet_path / "authors"
    if not authors_dir.exists():
        return []

    parquet_files = list(authors_dir.glob("*.parquet"))
    return sorted(parquet_files)


def migrate_authors_core(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_h_index: int = DEFAULT_MIN_H_INDEX,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate core author data with h-index filtering

    Returns dict with migration statistics
    """
    print(f"\n📚 Migrating core authors data (h-index >= {min_h_index})")

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table authors already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "authors",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table authors has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM authors")
    else:
        print("  📊 Table authors is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            # Process file in chunks to avoid memory issues
            file_start = time.time()

            # First get the total count for this file
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE summary_stats.h_index >= {min_h_index}
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records matching h-index >= {min_h_index} in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                insert_query = f"""
                INSERT OR IGNORE INTO authors (
                    id, orcid, display_name, display_name_alternatives,
                    works_count, cited_by_count, summary_stats, ids, latest_institutions
                )
                SELECT 
                    id,
                    orcid,
                    display_name,
                    display_name_alternatives,
                    works_count,
                    cited_by_count,
                    summary_stats,
                    ids,
                    list_transform(last_known_institutions, inst -> struct_pack(
                        id := inst.id,
                        display_name := inst.display_name,
                        country_code := inst.country_code
                    )) as latest_institutions
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE summary_stats.h_index >= {min_h_index}
                    LIMIT {chunk_size} OFFSET {offset}
                )
                """

                try:
                    conn.execute(insert_query)
                    print(
                        f"      📦 Processed chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(f"      ⚠️  Error in chunk {chunks_processed}: {e}")
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(f"    ✅ Added {file_rows:,} authors in {file_duration:.2f}s")

        duration = time.time() - start_time

        print("  🎉 Core authors migration completed!")
        print(f"    📊 Total authors migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "authors",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating authors: {e}")
        return {
            "table": "authors",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_author_topics(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_h_index: int = DEFAULT_MIN_H_INDEX,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate author-topic relationships from topic_share field

    Returns dict with migration statistics
    """
    print(f"\n🏷️  Migrating author-topic relationships")

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM author_topics").fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table author_topics already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "author_topics",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table author_topics has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM author_topics")
    else:
        print("  📊 Table author_topics is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            # Process file in chunks to avoid memory issues
            file_start = time.time()

            # First get the total count for this file
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE summary_stats.h_index >= {min_h_index}
                AND topic_share IS NOT NULL
                AND len(topic_share) > 0
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records with topics matching h-index >= {min_h_index} in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                insert_query = f"""
                INSERT INTO author_topics (author_id, topic_id, value)
                SELECT 
                    id as author_id,
                    unnest(topic_share).id as topic_id,
                    unnest(topic_share).value as value
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE summary_stats.h_index >= {min_h_index}
                        AND topic_share IS NOT NULL
                        AND len(topic_share) > 0
                    LIMIT {chunk_size} OFFSET {offset}
                )
                """

                try:
                    conn.execute(insert_query)
                    print(
                        f"      📦 Processed topics chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(f"      ⚠️  Error in topics chunk {chunks_processed}: {e}")
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute(
                "SELECT COUNT(*) FROM author_topics"
            ).fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(
                f"    ✅ Added {file_rows:,} topic relationships in {file_duration:.2f}s"
            )

        duration = time.time() - start_time

        print("  🎉 Author-topics migration completed!")
        print(f"    📊 Total relationships migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "author_topics",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating author_topics: {e}")
        return {
            "table": "author_topics",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_author_affiliations(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_h_index: int = DEFAULT_MIN_H_INDEX,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate author-institution relationships from affiliations field

    Returns dict with migration statistics
    """
    print(f"\n🏢 Migrating author-affiliation relationships")

    # Check if table already has data
    existing_count = conn.execute(
        "SELECT COUNT(*) FROM author_affiliations"
    ).fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table author_affiliations already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "author_affiliations",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table author_affiliations has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM author_affiliations")
    else:
        print("  📊 Table author_affiliations is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            # Process file in chunks to avoid memory issues
            file_start = time.time()

            # First get the total count for this file
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE summary_stats.h_index >= {min_h_index}
                AND affiliations IS NOT NULL
                AND len(affiliations) > 0
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records with affiliations matching h-index >= {min_h_index} in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                insert_query = f"""
                INSERT OR IGNORE INTO author_affiliations (author_id, institution_id, years)
                SELECT 
                    id as author_id,
                    unnest(affiliations).institution.id as institution_id,
                    unnest(affiliations).years as years
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE summary_stats.h_index >= {min_h_index}
                        AND affiliations IS NOT NULL
                        AND len(affiliations) > 0
                    LIMIT {chunk_size} OFFSET {offset}
                )
                """

                try:
                    conn.execute(insert_query)
                    print(
                        f"      📦 Processed affiliations chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(
                        f"      ⚠️  Error in affiliations chunk {chunks_processed}: {e}"
                    )
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute(
                "SELECT COUNT(*) FROM author_affiliations"
            ).fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(
                f"    ✅ Added {file_rows:,} affiliation relationships in {file_duration:.2f}s"
            )

        duration = time.time() - start_time

        print("  🎉 Author-affiliations migration completed!")
        print(f"    📊 Total relationships migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "author_affiliations",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating author_affiliations: {e}")
        return {
            "table": "author_affiliations",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_all_author_data(
    conn: duckdb.DuckDBPyConnection,
    parquet_path: Path,
    min_h_index: int = DEFAULT_MIN_H_INDEX,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> List[dict]:
    """
    Migrate all author-related data from parquet to DuckDB

    Returns list of migration statistics for each table
    """
    print(f"\n🚀 Starting Author Data Migration")
    print(f"📊 Minimum h-index filter: {min_h_index}")
    print("=" * 60)

    # Get parquet files for authors
    parquet_files = get_author_parquet_files(parquet_path)

    if not parquet_files:
        print("❌ No author parquet files found")
        return []

    print(f"📁 Found {len(parquet_files)} author parquet files")
    for pf in parquet_files:
        print(f"    - {pf.name} ({pf.stat().st_size:,} bytes)")

    results = []
    total_start_time = time.time()

    # Migrate in order: authors -> author_topics -> author_affiliations
    migrations = [
        ("authors", migrate_authors_core),
        ("author_topics", migrate_author_topics),
        # ("author_affiliations", migrate_author_affiliations),
    ]

    for table_name, migrate_func in migrations:
        result = migrate_func(
            conn, parquet_files, min_h_index, force_repopulate, chunk_size
        )
        results.append(result)

        # Stop if core authors migration fails
        if table_name == "authors" and result["status"] == "error":
            print("❌ Core authors migration failed, stopping")
            break

    total_duration = time.time() - total_start_time

    # Print summary
    print("\n📋 Migration Summary")
    print("=" * 60)

    successful = [r for r in results if r["status"] == "success"]
    skipped_populated = [r for r in results if r["status"] == "skipped_populated"]
    errors = [r for r in results if r["status"] == "error"]

    total_rows = sum(r["rows_migrated"] for r in results)

    print("📊 Overall Statistics:")
    print(f"   ✅ Successful migrations: {len(successful)}")
    print(f"   ⏭️  Skipped (populated): {len(skipped_populated)}")
    print(f"   ❌ Errors: {len(errors)}")
    print(f"   📊 Total rows migrated: {total_rows:,}")
    print(f"   ⏱️  Total time: {total_duration:.2f}s")

    if successful:
        print("\n✅ Successful Migrations:")
        for result in successful:
            print(
                f"  - {result['table']}: {result['rows_migrated']:,} rows ({result['duration_seconds']:.2f}s)"
            )

    if skipped_populated:
        print("\n⏭️  Skipped Tables (Already Populated):")
        for result in skipped_populated:
            print(
                f"  - {result['table']}: {result['rows_migrated']:,} rows (use --force to repopulate)"
            )

    if errors:
        print("\n❌ Failed Migrations:")
        for result in errors:
            error_msg = result.get("error", "Unknown error")
            print(f"  - {result['table']}: {error_msg}")

    return results


def get_author_table_stats(conn: duckdb.DuckDBPyConnection) -> None:
    """Print statistics for author-related tables"""
    print("\n📊 Author Table Statistics")
    print("=" * 60)

    tables = ["authors", "author_topics", "author_affiliations"]

    for table_name in tables:
        try:
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            print(f"  📋 {table_name}: {row_count:,} rows")

            # Show sample for authors table
            if table_name == "authors" and row_count > 0:
                sample = conn.execute(
                    f"SELECT display_name, summary_stats.h_index FROM {table_name} ORDER BY summary_stats.h_index DESC LIMIT 3"
                ).fetchall()
                print(f"      Top authors by h-index:")
                for name, h_idx in sample:
                    print(f"        - {name} (h-index: {h_idx})")

        except Exception as e:
            print(f"    ❌ {table_name}: Error getting count - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate OpenAlex authors from parquet files to DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Migrate all author data with default h-index filter (≥10)
    python migrate_authors.py
    
    # Use custom h-index threshold
    python migrate_authors.py --min-h-index 15
    
    # Migrate to specific database
    python migrate_authors.py --db-path /path/to/openalex.duckdb
    
    # Use different parquet source path
    python migrate_authors.py --parquet-path /path/to/parquet/files
    
    # Force repopulate tables that already have data
    python migrate_authors.py --force
        """,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="openalex.duckdb",
        help="Path to the DuckDB database file (default: openalex.duckdb)",
    )

    parser.add_argument(
        "--parquet-path",
        type=str,
        help=f"Path to parquet files directory (default: {parquet_destination_path})",
    )

    parser.add_argument(
        "--min-h-index",
        type=int,
        default=DEFAULT_MIN_H_INDEX,
        help=f"Minimum h-index to filter authors (default: {DEFAULT_MIN_H_INDEX})",
    )

    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show database statistics, do not migrate",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force repopulation of tables that already have data",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Number of records to process at once (default: {DEFAULT_CHUNK_SIZE:,})",
    )

    parser.add_argument(
        "--memory-limit",
        type=str,
        default="12GB",
        help="DuckDB memory limit (default: 12GB)",
    )

    args = parser.parse_args()

    # Resolve paths
    db_path = Path(args.db_path).resolve()

    if args.parquet_path:
        parquet_path = Path(args.parquet_path).resolve()
    else:
        parquet_path = parquet_destination_path

    # Verify paths exist
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        print("💡 Run setup_database.py first to create the database")
        sys.exit(1)

    if not parquet_path.exists():
        print(f"❌ Parquet directory not found: {parquet_path}")
        sys.exit(1)

    print("🚀 DuckDB OpenAlex Authors Migration")
    print("=" * 40)
    print(f"📁 Database file: {db_path}")
    print(f"📁 Parquet source: {parquet_path}")
    print(f"📊 Database size: {db_path.stat().st_size:,} bytes")
    print(f"📊 H-index filter: ≥ {args.min_h_index}")
    print(f"📦 Chunk size: {args.chunk_size:,} records")
    print(f"🧠 Memory limit: {args.memory_limit}")

    # Connect to database
    try:
        conn = duckdb.connect(str(db_path))
        print("✅ Connected to database")

        # Configure DuckDB for memory efficiency
        temp_dir = tempfile.mkdtemp(prefix="duckdb_temp_")
        print(f"🗂️  Using temporary directory: {temp_dir}")

        conn.execute(f"SET memory_limit='{args.memory_limit}';")
        conn.execute(f"SET temp_directory='{temp_dir}';")
        conn.execute("SET preserve_insertion_order=false;")
        conn.execute("SET max_temp_directory_size='10GB';")

        print("⚙️  Configured DuckDB memory settings")

    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    try:
        if args.stats_only:
            get_author_table_stats(conn)
        else:
            # Run migration
            migrate_all_author_data(
                conn=conn,
                parquet_path=parquet_path,
                min_h_index=args.min_h_index,
                force_repopulate=args.force,
                chunk_size=args.chunk_size,
            )

            # Show final database stats
            get_author_table_stats(conn)

    finally:
        conn.close()
        print("🔌 Database connection closed")


if __name__ == "__main__":
    main()
