#!/usr/bin/env python3
"""
Migrate OpenAlex Works from Parquet Files to DuckDB

This script specifically handles the works entity, extracting data from parquet files
and populating four tables:
1. works - core work information (filtered by is_paratext=false and citation_normalized_percentile.value >= 0.5)
2. work_sources - work-source relationships from primary_location and locations
3. authorships - work-author relationships from authorships
4. work_institutions - work-institution relationships through authorships

Usage:
    python migrate_works.py [--db-path path/to/database.duckdb] [--parquet-path path/to/parquet] [--min-percentile 0.5]
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

# Default minimum citation normalized percentile threshold for filtering
DEFAULT_MIN_PERCENTILE = 0.5

# Chunking configuration
DEFAULT_CHUNK_SIZE = (
    50_000  # Number of records to process at once (smaller for works due to complexity)
)


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def get_work_parquet_files(parquet_path: Path) -> List[Path]:
    """Get all parquet files for works entity"""
    works_dir = parquet_path / "works"
    if not works_dir.exists():
        return []

    parquet_files = list(works_dir.glob("*.parquet"))
    return sorted(parquet_files)


def migrate_works_core(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_percentile: float = DEFAULT_MIN_PERCENTILE,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate core work data with citation percentile and paratext filtering

    Returns dict with migration statistics
    """
    print(
        f"\n📚 Migrating core works data (percentile >= {min_percentile}, non-paratext, with authorships)"
    )

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table works already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "works",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table works has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM works")
    else:
        print("  📊 Table works is empty, proceeding with migration")

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
            WHERE is_paratext = false
                AND citation_normalized_percentile.value >= {min_percentile}
                AND authorships IS NOT NULL
                AND len(authorships) > 0
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(f"    ⏭️  No records matching criteria in {parquet_file.name}")
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                insert_query = f"""
                INSERT INTO works (
                    id, doi, title, display_name, publication_date, language, type, oa_url,
                    ids, primary_topic_id, citation_normalized_percentile_value, 
                    cited_by_count, fwci, authorships, created_date, updated_date
                )
                SELECT 
                    id,
                    doi,
                    title,
                    display_name,
                    publication_date,
                    language,
                    type,
                    open_access.oa_url as oa_url,
                    ids,
                    primary_topic.id as primary_topic_id,
                    citation_normalized_percentile.value as citation_normalized_percentile_value,
                    cited_by_count,
                    fwci,
                    list_transform(authorships, auth -> struct_pack(
                        author_position := auth.author_position,
                        author := struct_pack(
                            id := auth.author.id,
                            display_name := auth.author.display_name,
                            orcid := auth.author.orcid
                        ),
                        institutions := list_transform(auth.institutions, inst -> struct_pack(
                            id := inst.id,
                            display_name := inst.display_name
                        ))
                    )) as authorships,
                    created_date,
                    updated_date
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE is_paratext = false
                        AND citation_normalized_percentile.value >= {min_percentile}
                        AND authorships IS NOT NULL
                        AND len(authorships) > 0
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
            current_total = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(f"    ✅ Added {file_rows:,} works in {file_duration:.2f}s")

        duration = time.time() - start_time

        print("  🎉 Core works migration completed!")
        print(f"    📊 Total works migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "works",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating works: {e}")
        return {
            "table": "works",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_work_sources(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_percentile: float = DEFAULT_MIN_PERCENTILE,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate work-source relationships from primary_location and locations fields

    Returns dict with migration statistics
    """
    print(f"\n🔗 Migrating work-source relationships")

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM work_sources").fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table work_sources already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "work_sources",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table work_sources has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM work_sources")
    else:
        print("  📊 Table work_sources is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            file_start = time.time()

            # First get the total count for this file (works that match our criteria)
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE is_paratext = false
                AND citation_normalized_percentile.value >= {min_percentile}
                AND authorships IS NOT NULL
                AND len(authorships) > 0
                AND (
                    (primary_location.source.id IS NOT NULL) OR
                    (locations IS NOT NULL AND len(locations) > 0)
                )
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records with sources matching criteria in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert primary location sources
                primary_query = f"""
                INSERT INTO work_sources (
                    work_id, source_id, is_primary, is_oa, pdf_url, 
                    version, is_accepted, is_published
                )
                SELECT 
                    id as work_id,
                    primary_location.source.id as source_id,
                    true as is_primary,
                    primary_location.is_oa,
                    primary_location.pdf_url,
                    primary_location.version,
                    primary_location.is_accepted,
                    primary_location.is_published
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE is_paratext = false
                        AND citation_normalized_percentile.value >= {min_percentile}
                        AND authorships IS NOT NULL
                        AND len(authorships) > 0
                        AND primary_location.source.id IS NOT NULL
                    LIMIT {chunk_size} OFFSET {offset}
                )
                """

                # Insert other location sources
                locations_query = f"""
                INSERT INTO work_sources (
                    work_id, source_id, is_primary, is_oa, pdf_url, 
                    version, is_accepted, is_published
                )
                SELECT 
                    id as work_id,
                    unnest(locations).source.id as source_id,
                    false as is_primary,
                    unnest(locations).is_oa,
                    unnest(locations).pdf_url,
                    unnest(locations).version,
                    unnest(locations).is_accepted,
                    unnest(locations).is_published
                FROM (
                    SELECT * FROM read_parquet('{parquet_file}')
                    WHERE is_paratext = false
                        AND citation_normalized_percentile.value >= {min_percentile}
                        AND authorships IS NOT NULL
                        AND len(authorships) > 0
                        AND locations IS NOT NULL
                        AND len(locations) > 0
                    LIMIT {chunk_size} OFFSET {offset}
                )
                """

                try:
                    conn.execute(primary_query)
                    conn.execute(locations_query)
                    print(
                        f"      📦 Processed sources chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(f"      ⚠️  Error in sources chunk {chunks_processed}: {e}")
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute(
                "SELECT COUNT(*) FROM work_sources"
            ).fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(
                f"    ✅ Added {file_rows:,} source relationships in {file_duration:.2f}s"
            )

        duration = time.time() - start_time

        print("  🎉 Work-sources migration completed!")
        print(f"    📊 Total relationships migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "work_sources",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating work_sources: {e}")
        return {
            "table": "work_sources",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_authorships(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_percentile: float = DEFAULT_MIN_PERCENTILE,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate work-author relationships from authorships field

    Returns dict with migration statistics
    """
    print(f"\n👥 Migrating work-author relationships (authorships)")

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM authorships").fetchone()[0]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table authorships already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "authorships",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table authorships has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM authorships")
    else:
        print("  📊 Table authorships is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            file_start = time.time()

            # First get the total count for this file
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE is_paratext = false
                AND citation_normalized_percentile.value >= {min_percentile}
                AND authorships IS NOT NULL
                AND len(authorships) > 0
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records with authorships matching criteria in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                insert_query = f"""
                WITH filtered_works AS (
                    SELECT 
                        id,
                        authorships
                    FROM read_parquet('{parquet_file}')
                    WHERE is_paratext = false
                        AND citation_normalized_percentile.value >= {min_percentile}
                        AND authorships IS NOT NULL
                        AND len(authorships) > 0
                    LIMIT {chunk_size} OFFSET {offset}
                ),
                unnested_authorships AS (
                    SELECT 
                        fw.id as work_id,
                        unnest(fw.authorships) as authorship
                    FROM filtered_works fw
                )
                INSERT INTO authorships (work_id, author_id)
                SELECT 
                    ua.work_id,
                    ua.authorship.author.id as author_id,
                FROM unnested_authorships ua
                WHERE ua.authorship.author.id IS NOT NULL
                """

                try:
                    conn.execute(insert_query)
                    print(
                        f"      📦 Processed authorships chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(
                        f"      ⚠️  Error in authorships chunk {chunks_processed}: {e}"
                    )
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute("SELECT COUNT(*) FROM authorships").fetchone()[
                0
            ]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(
                f"    ✅ Added {file_rows:,} authorship relationships in {file_duration:.2f}s"
            )

        duration = time.time() - start_time

        print("  🎉 Authorships migration completed!")
        print(f"    📊 Total relationships migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "authorships",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating authorships: {e}")
        return {
            "table": "authorships",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_work_institutions(
    conn: duckdb.DuckDBPyConnection,
    parquet_files: List[Path],
    min_percentile: float = DEFAULT_MIN_PERCENTILE,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Migrate work-institution relationships from authorships.institutions field

    Returns dict with migration statistics
    """
    print(f"\n🏢 Migrating work-institution relationships")

    # Check if table already has data
    existing_count = conn.execute("SELECT COUNT(*) FROM work_institutions").fetchone()[
        0
    ]

    if existing_count > 0 and not force_repopulate:
        print(
            f"  ⏭️  Table work_institutions already has {existing_count:,} rows, skipping (use --force to repopulate)"
        )
        return {
            "table": "work_institutions",
            "rows_migrated": existing_count,
            "status": "skipped_populated",
        }

    if existing_count > 0:
        print(
            f"  🗑️  Table work_institutions has {existing_count:,} rows, truncating due to --force flag"
        )
        conn.execute("DELETE FROM work_institutions")
    else:
        print("  📊 Table work_institutions is empty, proceeding with migration")

    start_time = time.time()
    total_rows = 0

    try:
        for i, parquet_file in enumerate(parquet_files, 1):
            print(f"  📄 Processing file {i}/{len(parquet_files)}: {parquet_file.name}")

            file_start = time.time()

            # First get the total count for this file
            count_query = f"""
            SELECT COUNT(*) FROM read_parquet('{parquet_file}')
            WHERE is_paratext = false
                AND citation_normalized_percentile.value >= {min_percentile}
                AND authorships IS NOT NULL
                AND len(authorships) > 0
            """
            total_file_records = conn.execute(count_query).fetchone()[0]

            if total_file_records == 0:
                print(
                    f"    ⏭️  No records with institutions matching criteria in {parquet_file.name}"
                )
                continue

            # Process in chunks
            chunks_processed = 0

            for offset in range(0, total_file_records, chunk_size):
                chunks_processed += 1

                # Insert chunk with IGNORE for duplicates
                # This query flattens the nested structure: work -> authorship -> institutions
                insert_query = f"""
                WITH filtered_works AS (
                    SELECT 
                        id,
                        authorships
                    FROM read_parquet('{parquet_file}')
                    WHERE is_paratext = false
                        AND citation_normalized_percentile.value >= {min_percentile}
                        AND authorships IS NOT NULL
                        AND len(authorships) > 0
                    LIMIT {chunk_size} OFFSET {offset}
                ),
                unnested_authorships AS (
                    SELECT 
                        fw.id as work_id,
                        unnest(fw.authorships) as authorship
                    FROM filtered_works fw
                ),
                unnested_institutions AS (
                    SELECT 
                        ua.work_id,
                        ua.authorship.author.id as author_id,
                        unnest(ua.authorship.institutions) as institution
                    FROM unnested_authorships ua
                    WHERE ua.authorship.author.id IS NOT NULL
                        AND ua.authorship.institutions IS NOT NULL
                        AND len(ua.authorship.institutions) > 0
                )
                INSERT OR IGNORE INTO work_institutions (work_id, author_id, institution_id)
                SELECT 
                    ui.work_id,
                    ui.author_id,
                    ui.institution.id as institution_id
                FROM unnested_institutions ui
                WHERE ui.institution.id IS NOT NULL
                """

                try:
                    conn.execute(insert_query)
                    print(
                        f"      📦 Processed institutions chunk {chunks_processed} (offset {offset})"
                    )
                except Exception as e:
                    print(
                        f"      ⚠️  Error in institutions chunk {chunks_processed}: {e}"
                    )
                    continue

            file_duration = time.time() - file_start

            # Get count of rows added from this file
            current_total = conn.execute(
                "SELECT COUNT(*) FROM work_institutions"
            ).fetchone()[0]
            file_rows = current_total - total_rows
            total_rows = current_total

            print(
                f"    ✅ Added {file_rows:,} institution relationships in {file_duration:.2f}s"
            )

        duration = time.time() - start_time

        print("  🎉 Work-institutions migration completed!")
        print(f"    📊 Total relationships migrated: {total_rows:,}")
        print(f"    ⏱️  Total duration: {duration:.2f}s")
        print(f"    🚀 Rate: {total_rows / duration:,.0f} rows/second")

        return {
            "table": "work_institutions",
            "rows_migrated": total_rows,
            "duration_seconds": duration,
            "status": "success",
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Error migrating work_institutions: {e}")
        return {
            "table": "work_institutions",
            "rows_migrated": 0,
            "duration_seconds": duration,
            "status": "error",
            "error": str(e),
        }


def migrate_all_work_data(
    conn: duckdb.DuckDBPyConnection,
    parquet_path: Path,
    min_percentile: float = DEFAULT_MIN_PERCENTILE,
    force_repopulate: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> List[dict]:
    """
    Migrate all work-related data from parquet to DuckDB

    Returns list of migration statistics for each table
    """
    print(f"\n🚀 Starting Work Data Migration")
    print(f"📊 Minimum citation percentile filter: {min_percentile}")
    print(f"🚫 Filtering out paratexts")
    print(f"👥 Filtering out works without authorships")
    print("=" * 60)

    # Get parquet files for works
    parquet_files = get_work_parquet_files(parquet_path)

    if not parquet_files:
        print("❌ No work parquet files found")
        return []

    print(f"📁 Found {len(parquet_files)} work parquet files")
    for pf in parquet_files:
        print(f"    - {pf.name} ({pf.stat().st_size:,} bytes)")

    results = []
    total_start_time = time.time()

    # Migrate in order: works -> work_sources -> authorships -> work_institutions
    migrations = [
        ("works", migrate_works_core),
        ("work_sources", migrate_work_sources),
        ("authorships", migrate_authorships),
        # ("work_institutions", migrate_work_institutions),
    ]

    for table_name, migrate_func in migrations:
        result = migrate_func(
            conn, parquet_files, min_percentile, force_repopulate, chunk_size
        )
        results.append(result)

        # Stop if core works migration fails
        if table_name == "works" and result["status"] == "error":
            print("❌ Core works migration failed, stopping")
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


def check_missing_relationships(conn: duckdb.DuckDBPyConnection) -> None:
    """Check for works without authorships or sources and show samples"""
    print("\n🔍 Missing Relationships Analysis")
    print("=" * 60)

    try:
        # Check works without authorships
        works_without_authorships = conn.execute("""
            SELECT COUNT(*) FROM works w
            WHERE NOT EXISTS (
                SELECT 1 FROM authorships a WHERE a.work_id = w.id
            )
        """).fetchone()[0]

        print(f"  📝 Works without authorships: {works_without_authorships:,}")

        if works_without_authorships > 0:
            # Get sample of works without authorships
            sample_no_authors = conn.execute("""
                SELECT w.id, w.display_name
                FROM works w
                WHERE NOT EXISTS (
                    SELECT 1 FROM authorships a WHERE a.work_id = w.id
                )
                LIMIT 5
            """).fetchall()

            print("      Sample works without authorships:")
            for work_id, title in sample_no_authors:
                title_truncated = title[:60] + "..." if len(title) > 60 else title
                print(f"        - {work_id}: {title_truncated}")

        # Check works without sources
        works_without_sources = conn.execute("""
            SELECT COUNT(*) FROM works w
            WHERE NOT EXISTS (
                SELECT 1 FROM work_sources ws WHERE ws.work_id = w.id
            )
        """).fetchone()[0]

        print(f"  📚 Works without sources: {works_without_sources:,}")

        if works_without_sources > 0:
            # Get sample of works without sources
            sample_no_sources = conn.execute("""
                SELECT w.id, w.display_name
                FROM works w
                WHERE NOT EXISTS (
                    SELECT 1 FROM work_sources ws WHERE ws.work_id = w.id
                )
                LIMIT 5
            """).fetchall()

            print("      Sample works without sources:")
            for work_id, title in sample_no_sources:
                title_truncated = title[:60] + "..." if len(title) > 60 else title
                print(f"        - {work_id}: {title_truncated}")

        # Calculate coverage percentages
        total_works = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        if total_works > 0:
            authorship_coverage = (
                (total_works - works_without_authorships) / total_works
            ) * 100
            source_coverage = (
                (total_works - works_without_sources) / total_works
            ) * 100

            print(f"\n  📊 Coverage Statistics:")
            print(
                f"      Authorship coverage: {authorship_coverage:.1f}% ({total_works - works_without_authorships:,}/{total_works:,})"
            )
            print(
                f"      Source coverage: {source_coverage:.1f}% ({total_works - works_without_sources:,}/{total_works:,})"
            )

    except Exception as e:
        print(f"    ❌ Error checking missing relationships: {e}")


def get_work_table_stats(conn: duckdb.DuckDBPyConnection) -> None:
    """Print statistics for work-related tables"""
    print("\n📊 Work Table Statistics")
    print("=" * 60)

    tables = ["works", "work_sources", "authorships", "work_institutions"]

    for table_name in tables:
        try:
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            print(f"  📋 {table_name}: {row_count:,} rows")

            # Show sample for works table
            if table_name == "works" and row_count > 0:
                sample = conn.execute(
                    f"SELECT display_name, citation_normalized_percentile_value FROM {table_name} ORDER BY citation_normalized_percentile_value DESC LIMIT 3"
                ).fetchall()
                print(f"      Top works by citation percentile:")
                for name, percentile in sample:
                    print(f"        - {name[:50]}... (percentile: {percentile:.3f})")

        except Exception as e:
            print(f"    ❌ {table_name}: Error getting count - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate OpenAlex works from parquet files to DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Migrate all work data with default percentile filter (≥0.5)
    python migrate_works.py
    
    # Use custom percentile threshold
    python migrate_works.py --min-percentile 0.7
    
    # Migrate to specific database
    python migrate_works.py --db-path /path/to/openalex.duckdb
    
    # Use different parquet source path
    python migrate_works.py --parquet-path /path/to/parquet/files
    
    # Force repopulate tables that already have data
    python migrate_works.py --force
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
        "--min-percentile",
        type=float,
        default=DEFAULT_MIN_PERCENTILE,
        help=f"Minimum citation normalized percentile to filter works (default: {DEFAULT_MIN_PERCENTILE})",
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

    print("🚀 DuckDB OpenAlex Works Migration")
    print("=" * 40)
    print(f"📁 Database file: {db_path}")
    print(f"📁 Parquet source: {parquet_path}")
    print(f"📊 Database size: {db_path.stat().st_size:,} bytes")
    print(f"📊 Citation percentile filter: ≥ {args.min_percentile}")
    print(f"🚫 Paratext filter: exclude paratexts")
    print(f"👥 Authorship filter: exclude works without authorships")
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
            check_missing_relationships(conn)
            get_work_table_stats(conn)
        else:
            # Run migration
            migrate_all_work_data(
                conn=conn,
                parquet_path=parquet_path,
                min_percentile=args.min_percentile,
                force_repopulate=args.force,
                chunk_size=args.chunk_size,
            )

            # Show final database stats
            check_missing_relationships(conn)
            get_work_table_stats(conn)

    finally:
        conn.close()
        print("🔌 Database connection closed")


if __name__ == "__main__":
    main()
