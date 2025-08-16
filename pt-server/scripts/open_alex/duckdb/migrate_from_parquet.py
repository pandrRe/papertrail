#!/usr/bin/env python3
"""
Migrate OpenAlex Parquet Files to DuckDB

This script reads parquet files from the parquet_destination_path and populates
the corresponding DuckDB tables. It's designed to be idempotent by truncating
tables before inserting new data.

Usage:
    python migrate_from_parquet.py [--db-path path/to/database.duckdb] [--parquet-path path/to/parquet]
"""

import argparse
import sys
from pathlib import Path
import duckdb
import time
from typing import List, Optional

# Hardcoded parquet destination path (same as in open_alex_parquet.py)
parquet_destination_path = Path("/Volumes/T7/openalex-parquet")

# Define all available entities based on the SQL schema
ALL_ENTITIES = [
    "authors",
    "subfields",
    "publishers",
    "sources",
    "funders",
    "institutions",
    "concepts",
    "domains",
    "fields",
    "topics",
]


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def get_entity_parquet_files(parquet_path: Path, entity: str) -> List[Path]:
    """Get all parquet files for a specific entity"""
    entity_dir = parquet_path / entity
    if not entity_dir.exists():
        return []

    parquet_files = list(entity_dir.glob("*.parquet"))
    return sorted(parquet_files)


def migrate_entity(
    conn: duckdb.DuckDBPyConnection,
    parquet_path: Path,
    entity: str,
    force_repopulate: bool = False,
) -> dict:
    """
    Migrate a single entity from parquet files to DuckDB table

    Returns dict with migration statistics
    """
    print(f"\n= Migrating entity: {entity}")

    # Get parquet files for this entity
    parquet_files = get_entity_parquet_files(parquet_path, entity)

    if not parquet_files:
        print(f"  �  No parquet files found for {entity}")
        return {
            "entity": entity,
            "files_found": 0,
            "rows_migrated": 0,
            "duration_seconds": 0,
            "status": "skipped",
        }

    print(f"  =� Found {len(parquet_files)} parquet files")
    for pf in parquet_files:
        print(f"    - {pf.name} ({pf.stat().st_size:,} bytes)")

    start_time = time.time()

    try:
        # Truncate the table first for idempotency
        print(f"  =�  Truncating table {entity}")
        # Check if table already has data
        existing_count = conn.execute(f"SELECT COUNT(*) FROM {entity}").fetchone()[0]

        if existing_count > 0 and not force_repopulate:
            print(
                f"  ⏭️  Table {entity} already has {existing_count:,} rows, skipping (use --force to repopulate)"
            )
            return {
                "entity": entity,
                "files_found": len(parquet_files),
                "rows_migrated": existing_count,
                "duration_seconds": 0,
                "status": "skipped_populated",
            }

        if existing_count > 0:
            print(
                f"  🗑️  Table {entity} has {existing_count:,} rows, truncating due to --force flag"
            )
            conn.execute(f"DELETE FROM {entity}")
        else:
            print(f"  📊 Table {entity} is empty, proceeding with migration")

        total_rows = 0

        # Process each parquet file
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  =� Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            # Get row count first
            row_count_query = f"SELECT COUNT(*) FROM read_parquet('{parquet_file}')"
            file_row_count = conn.execute(row_count_query).fetchone()[0]
            print(f"    =� File contains {file_row_count:,} rows")

            # Insert data from parquet file
            insert_query = f"""
            INSERT INTO {entity} 
            SELECT * FROM read_parquet('{parquet_file}')
            """

            file_start = time.time()
            conn.execute(insert_query)
            file_duration = time.time() - file_start

            total_rows += file_row_count

            print(f"     Inserted {file_row_count:,} rows in {file_duration:.2f}s")
            print(f"    =� Rate: {file_row_count / file_duration:,.0f} rows/second")

        # Verify final count
        final_count = conn.execute(f"SELECT COUNT(*) FROM {entity}").fetchone()[0]
        duration = time.time() - start_time

        print("   Migration completed!")
        print(f"    =� Total rows migrated: {final_count:,}")
        print(f"    �  Total duration: {duration:.2f}s")
        print(f"    =� Overall rate: {final_count / duration:,.0f} rows/second")

        # Show table head
        print("  =@ Table head (first 5 rows):")
        try:
            head_result = conn.execute(f"SELECT * FROM {entity} LIMIT 5").fetchall()
            columns = [desc[0] for desc in conn.description]

            # Print column headers
            print(
                f"    =� Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}"
            )

            # Print sample rows (showing first few columns to avoid clutter)
            for row_idx, row in enumerate(head_result, 1):
                row_preview = str(row[:3]) + "..." if len(row) > 3 else str(row)
                print(f"    {row_idx}. {row_preview}")

        except Exception as e:
            print(f"    �  Could not fetch table head: {e}")

        return {
            "entity": entity,
            "files_found": len(parquet_files),
            "rows_migrated": final_count,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  L Error migrating {entity}: {e}")

        return {
            "entity": entity,
            "files_found": len(parquet_files),
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_all_entities(
    conn: duckdb.DuckDBPyConnection,
    parquet_path: Path,
    exclude: Optional[List[str]] = None,
    include_only: Optional[List[str]] = None,
    force_repopulate: bool = False,
) -> List[dict]:
    """
    Migrate all entities from parquet to DuckDB

    Returns list of migration statistics for each entity
    """
    if exclude is None:
        exclude = []

    # Determine which entities to process
    entities_to_process = []

    for entity in ALL_ENTITIES:
        # Skip if in exclude list
        if entity in exclude:
            print(f"�  Excluding {entity} (in exclude list)")
            continue

        # If include_only is set, only include entities in that list
        if include_only is not None and entity not in include_only:
            print(f"�  Skipping {entity} (not in include_only list)")
            continue

        entities_to_process.append(entity)

    print(f"\n=� Entities to migrate: {', '.join(entities_to_process)}")
    if exclude:
        print(f"=� Excluded: {', '.join(exclude)}")

    # Process each entity
    results = []
    total_start_time = time.time()

    for entity in entities_to_process:
        result = migrate_entity(conn, parquet_path, entity, force_repopulate)
        results.append(result)

    total_duration = time.time() - total_start_time

    # Print summary
    print("\n<� Migration Summary")
    print(f"{'=' * 60}")

    successful = [r for r in results if r["status"] == "success"]
    skipped = [r for r in results if r["status"] == "skipped"]
    skipped_populated = [r for r in results if r["status"] == "skipped_populated"]
    errors = [r for r in results if r["status"] == "error"]

    total_rows = sum(r["rows_migrated"] for r in successful)
    total_files = sum(r["files_found"] for r in results)

    print("=� Overall Statistics:")
    print(f"   Successful migrations: {len(successful)}")
    print(f"  �  Skipped (no files): {len(skipped)}")
    print(f"  L Errors: {len(errors)}")
    print(f"  =� Total files processed: {total_files}")
    print(f"  =� Total rows migrated: {total_rows:,}")
    print(f"  �  Total time: {total_duration:.2f}s")
    if total_rows > 0:
        print(f"  =� Overall rate: {total_rows / total_duration:,.0f} rows/second")

    if successful:
        print("\n Successful Migrations:")
        for result in successful:
            print(
                f"  - {result['entity']}: {result['rows_migrated']:,} rows ({result['duration_seconds']:.2f}s)"
            )

    if skipped:
        print("\n�  Skipped Entities:")
        for result in skipped:
            print(f"  - {result['entity']}: No parquet files found")

    if skipped_populated:
        print("\n🔄 Skipped Entities (Already Populated):")
        for result in skipped_populated:
            print(
                f"  - {result['entity']}: {result['rows_migrated']:,} rows (use --force to repopulate)"
            )

    if errors:
        print("\nL Failed Migrations:")
        for result in errors:
            error_msg = result.get("error", "Unknown error")
            print(f"  - {result['entity']}: {error_msg}")

    return results


def get_table_stats(conn: duckdb.DuckDBPyConnection) -> None:
    """Print statistics for all tables in the database"""
    print("\n=� Database Table Statistics")
    print(f"{'=' * 60}")

    try:
        # Get all table names
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'main' 
        ORDER BY table_name
        """
        tables = conn.execute(tables_query).fetchall()

        if not tables:
            print("  =� No tables found in database")
            return

        print(f"  =� Found {len(tables)} tables:")

        total_rows = 0
        for (table_name,) in tables:
            try:
                count_result = conn.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()
                row_count = count_result[0] if count_result else 0
                total_rows += row_count

                print(f"    - {table_name}: {row_count:,} rows")

            except Exception as e:
                print(f"    - {table_name}: Error getting count - {e}")

        print(f"\n  =� Total rows across all tables: {total_rows:,}")

    except Exception as e:
        print(f"  L Error getting table statistics: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate OpenAlex parquet files to DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Migrate all entities
    python migrate_from_parquet.py
    
    # Migrate to specific database
    python migrate_from_parquet.py --db-path /path/to/openalex.duckdb
    
    # Migrate only specific entities
    python migrate_from_parquet.py --include-only authors,topics
    
    # Migrate all except specific entities
    python migrate_from_parquet.py --exclude works,concepts
    
    # Use different parquet source path
    python migrate_from_parquet.py --parquet-path /path/to/parquet/files
    
    # Force repopulate tables that already have data
    python migrate_from_parquet.py --force
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
        "--include-only",
        type=str,
        help='Comma-separated list of entities to include (e.g., "authors,topics")',
    )

    parser.add_argument(
        "--exclude",
        type=str,
        help='Comma-separated list of entities to exclude (e.g., "works,concepts")',
    )

    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show database statistics, do not migrate",
    )

    parser.add_argument(
        "--list-entities",
        action="store_true",
        help="List all available entities and exit",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force repopulation of tables that already have data",
    )

    args = parser.parse_args()

    # Handle list entities
    if args.list_entities:
        print("Available entities:")
        for entity in ALL_ENTITIES:
            print(f"  - {entity}")
        return

    # Parse include/exclude lists
    include_only = None
    if args.include_only:
        include_only = [e.strip() for e in args.include_only.split(",")]

    exclude = None
    if args.exclude:
        exclude = [e.strip() for e in args.exclude.split(",")]

    # Validate entity names
    if include_only:
        invalid = [e for e in include_only if e not in ALL_ENTITIES]
        if invalid:
            print(f"L Invalid entities in include_only: {', '.join(invalid)}")
            print(f"Available entities: {', '.join(ALL_ENTITIES)}")
            sys.exit(1)

    if exclude:
        invalid = [e for e in exclude if e not in ALL_ENTITIES]
        if invalid:
            print(f"L Invalid entities in exclude: {', '.join(invalid)}")
            print(f"Available entities: {', '.join(ALL_ENTITIES)}")
            sys.exit(1)

    # Resolve paths
    db_path = Path(args.db_path).resolve()

    if args.parquet_path:
        parquet_path = Path(args.parquet_path).resolve()
    else:
        parquet_path = parquet_destination_path

    # Verify paths exist
    if not db_path.exists():
        print(f"L Database file not found: {db_path}")
        print("=� Run setup_database.py first to create the database")
        sys.exit(1)

    if not parquet_path.exists():
        print(f"L Parquet directory not found: {parquet_path}")
        sys.exit(1)

    print("DuckDB OpenAlex Migration")
    print("=" * 40)
    print(f"Database file: {db_path}")
    print(f"Parquet source: {parquet_path}")
    print(f"Database size: {db_path.stat().st_size:,} bytes")

    if include_only:
        print(f"Include only: {', '.join(include_only)}")
    if exclude:
        print(f"Exclude: {', '.join(exclude)}")

    # Connect to database
    try:
        conn = duckdb.connect(str(db_path))
        print(" Connected to database")
    except Exception as e:
        print(f"L Failed to connect to database: {e}")
        sys.exit(1)

    try:
        if args.stats_only:
            get_table_stats(conn)
        else:
            # Run migration
            migrate_all_entities(
                conn=conn,
                parquet_path=parquet_path,
                exclude=exclude,
                include_only=include_only,
                force_repopulate=args.force,
            )

            # Show final database stats
            get_table_stats(conn)

    finally:
        conn.close()
        print("Database connection closed")


if __name__ == "__main__":
    main()
