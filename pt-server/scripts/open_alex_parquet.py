import os
import gzip
import json
import sys
import time
import threading
from pathlib import Path
import polars as pl

# Enable verbose logging for Polars
pl.Config.set_verbose(True)
pl.Config.set_streaming_chunk_size(10_000)

openalex_source_path = Path("/Volumes/T7/openalex-snapshot/data")
parquet_destination_path = Path("/Volumes/T7/openalex-parquet")

os.makedirs(parquet_destination_path, exist_ok=True)


def process_entity_to_parquet(entity_name: str, filter_fn=None) -> None:
    """
    Processes a specific entity (authors, topics, etc.) converting
    all .gz files to a single parquet file per date folder.

    Args:
        entity_name: Name of the entity (authors, topics, concepts, etc.)
        filter_fn: Optional function to filter records. Takes a JSON record and returns True/False.
    """
    source_entity_path = openalex_source_path / entity_name
    dest_entity_path = parquet_destination_path / entity_name

    # Create destination directory
    os.makedirs(dest_entity_path, exist_ok=True)

    if not source_entity_path.exists():
        print(f"⚠️  Folder {entity_name} not found in source path")
        return

    print(f"🔄 Processing entity: {entity_name}")

    # Clean up any temporary files from previous failed runs
    cleanup_temp_files(dest_entity_path)

    # Find all updated_date folders
    date_folders = [
        d
        for d in source_entity_path.iterdir()
        if d.is_dir() and d.name.startswith("updated_date=")
    ]

    for date_folder in sorted(date_folders):
        date_name = date_folder.name  # updated_date=2023-05-17
        output_file = dest_entity_path / f"{date_name}.parquet"

        # Skip if file already exists
        if output_file.exists():
            print(f"  ⏭️  Skipping {date_name} - file already exists")
            continue

        print(f"  📁 Processing {date_name}")

        # Find all .gz files in the folder
        gz_files = list(date_folder.glob("*.gz"))

        if not gz_files:
            print(f"    ⚠️  No .gz files found in {date_name}")
            continue

        try:
            # Create temporary JSONL file
            temp_jsonl_file = dest_entity_path / f"{date_name}.jsonl"

            print(f"    📄 Creating temporary JSONL file: {temp_jsonl_file.name}")
            if filter_fn is not None:
                print(
                    "    🔍 Filter function provided - will filter records during processing"
                )

            # Stream .gz files to temporary JSONL file
            record_count = 0
            filtered_count = 0
            with open(temp_jsonl_file, "w", encoding="utf-8") as temp_file:
                for gz_file in gz_files:
                    print(f"    🗄️ Extracting {gz_file.name}")
                    with gzip.open(gz_file, "rt", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():  # Ignore empty lines
                                try:
                                    # Validate JSON by parsing it
                                    record = json.loads(line.strip())

                                    # Apply filter function if provided
                                    if filter_fn is not None:
                                        if not filter_fn(record):
                                            filtered_count += 1
                                            continue  # Skip this record

                                    temp_file.write(line.strip() + "\n")
                                    record_count += 1
                                except json.JSONDecodeError as e:
                                    print(f"      ⚠️  Error decoding JSON: {e}")
                                    continue

            if record_count == 0:
                print(f"    ⚠️  No valid records found in {date_name}")
                if filter_fn is not None and filtered_count > 0:
                    print(f"    📊 {filtered_count} records were filtered out")
                temp_jsonl_file.unlink()  # Remove empty temp file
                continue

            # Log filtering statistics if applicable
            if filter_fn is not None and filtered_count > 0:
                print(
                    f"    📊 Filtered out {filtered_count} records, kept {record_count} records"
                )

            # Convert JSONL to Parquet using Polars streaming
            print(f"    💾 Converting {record_count} records from JSONL to Parquet")

            # Create temporary parquet file with .tmp extension
            temp_parquet_file = output_file.with_suffix(".parquet.tmp")

            try:
                print(f"    🔍 Starting Polars scan_ndjson for {temp_jsonl_file.name}")
                print(
                    f"    📏 JSONL file size: {temp_jsonl_file.stat().st_size:,} bytes"
                )

                # System resource information
                try:
                    import psutil

                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage(str(temp_parquet_file.parent))

                    print(
                        f"    🧠 Available RAM: {memory.available / 1024 / 1024 / 1024:.1f} GB"
                    )
                    print(
                        f"    💾 Available disk space: {disk.free / 1024 / 1024 / 1024:.1f} GB"
                    )
                    print(f"    📊 Record count to process: {record_count:,}")
                except ImportError:
                    print(
                        "    ℹ️  psutil not available - skipping system resource check"
                    )

                # Import for detailed logging (already imported globally)
                start_time = time.time()

                # Force flush to ensure logs appear immediately
                sys.stdout.flush()

                # Create lazy frame first with verbose logging
                print("    🧠 Creating lazy DataFrame with conservative settings...")
                sys.stdout.flush()

                lazy_df = pl.scan_ndjson(
                    str(temp_jsonl_file),
                    infer_schema_length=1_000,  # Reduced from 100,000 to save memory
                    low_memory=True,
                )

                schema_time = time.time()
                print(
                    f"    📊 Schema inference completed in {schema_time - start_time:.2f}s"
                )
                print(f"    📊 Writing to {temp_parquet_file.name}")
                print(
                    "    🔧 Using conservative settings: row_group_size=5,000, infer_schema_length=1,000"
                )
                sys.stdout.flush()

                # Add progress callback if possible and more detailed logging
                print("    💾 Starting sink_parquet operation...")
                print("    ⏱️  This may take a while for large files - please wait...")
                print("    📊 Starting progress monitor (updates every 30s)...")
                sys.stdout.flush()

                # Start progress monitoring
                monitor_thread = monitor_sink_progress(temp_parquet_file, interval=30)

                sink_start_time = time.time()

                # Write to temporary Parquet file with more conservative settings
                lazy_df.sink_parquet(
                    str(temp_parquet_file),
                    compression="snappy",
                    row_group_size=1_000,  # Reduced from 10,000 to use less memory
                )

                sink_end_time = time.time()
                total_time = sink_end_time - start_time
                sink_time = sink_end_time - sink_start_time

                print(f"    ✅ Parquet file written successfully in {sink_time:.2f}s")
                print(f"    📊 Total conversion time: {total_time:.2f}s")
                print(
                    f"    📏 Output file size: {temp_parquet_file.stat().st_size:,} bytes"
                )

                # Calculate compression ratio
                compression_ratio = (
                    temp_jsonl_file.stat().st_size / temp_parquet_file.stat().st_size
                )
                print(f"    📦 Compression ratio: {compression_ratio:.2f}x")

            except pl.exceptions.ComputeError as e:
                print(f"    ❌ Polars compute error during sink_parquet: {e}")
                print(f"    📊 Record count: {record_count}")
                print(f"    📁 JSONL file size: {temp_jsonl_file.stat().st_size} bytes")
                raise
            except pl.exceptions.SchemaError as e:
                print(f"    ❌ Polars schema error: {e}")
                print(
                    "    💡 Try reducing infer_schema_length or check data consistency"
                )
                raise
            except MemoryError as e:
                print(f"    ❌ Memory error during conversion: {e}")
                print(f"    📊 Record count: {record_count}")
                print("    💡 Consider processing smaller batches")
                raise
            except OSError as e:
                print(f"    ❌ OS/IO error during file write: {e}")
                print("    💿 Check disk space and permissions")
                raise
            except Exception as e:
                print(
                    f"    ❌ Unexpected error during sink_parquet: {type(e).__name__}: {e}"
                )
                print(f"    📊 Record count: {record_count}")
                print(f"    📁 JSONL file: {temp_jsonl_file}")
                print(f"    📁 Target parquet: {temp_parquet_file}")
                raise

            # Rename temporary parquet file to final name only after successful conversion
            print(f"    🔄 Renaming {temp_parquet_file.name} to {output_file.name}")
            temp_parquet_file.rename(output_file)

            print(f"    ✅ Saved: {output_file} ({record_count} records)")

            # Clean up temporary file
            temp_jsonl_file.unlink()
            print(f"    🗑️  Removed temporary file: {temp_jsonl_file.name}")

        except Exception as e:
            print(f"    ❌ Error processing {date_name}: {e}")

            # Clean up temporary and output files on error
            if "temp_jsonl_file" in locals() and temp_jsonl_file.exists():
                temp_jsonl_file.unlink()
                print(f"    🗑️  Cleaned up temporary file: {temp_jsonl_file.name}")

            # Clean up temporary parquet file if it exists
            temp_parquet_file = output_file.with_suffix(".parquet.tmp")
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
                print(
                    f"    🗑️  Cleaned up temporary parquet file: {temp_parquet_file.name}"
                )

            # Clean up final parquet file if it exists (shouldn't happen with .tmp approach, but safety)
            if output_file.exists():
                output_file.unlink()
                print(f"    🗑️  Cleaned up incomplete parquet file: {output_file.name}")

            continue


def cleanup_temp_files(dest_entity_path: Path) -> None:
    """
    Clean up any temporary files (.parquet.tmp, .jsonl, and .csv) from previous failed runs.

    Args:
        dest_entity_path: Path to the entity destination directory
    """
    temp_files_removed = 0

    # Find and remove .parquet.tmp files
    tmp_parquet_files = list(dest_entity_path.glob("*.parquet.tmp"))
    for tmp_file in tmp_parquet_files:
        try:
            tmp_file.unlink()
            print(f"    🗑️  Removed temporary parquet file: {tmp_file.name}")
            temp_files_removed += 1
        except Exception as e:
            print(f"    ⚠️  Failed to remove {tmp_file.name}: {e}")

    # Find and remove .jsonl files
    jsonl_files = list(dest_entity_path.glob("*.jsonl"))
    for jsonl_file in jsonl_files:
        try:
            jsonl_file.unlink()
            print(f"    🗑️  Removed hanging JSONL file: {jsonl_file.name}")
            temp_files_removed += 1
        except Exception as e:
            print(f"    ⚠️  Failed to remove {jsonl_file.name}: {e}")

    # Find and remove .csv files (for merged_ids processing)
    csv_files = list(dest_entity_path.glob("*.csv"))
    for csv_file in csv_files:
        try:
            csv_file.unlink()
            print(f"    🗑️  Removed hanging CSV file: {csv_file.name}")
            temp_files_removed += 1
        except Exception as e:
            print(f"    ⚠️  Failed to remove {csv_file.name}: {e}")

    if temp_files_removed > 0:
        print(f"    ✅ Cleaned up {temp_files_removed} temporary files")
    else:
        print("    ✨ No temporary files found to clean up")


def convert_all_entities(
    exclude: list[str] = None, include_only: list[str] = None, filter_fn=None
) -> None:
    """
    Finds all entities in the source directory and processes each one.

    Args:
        exclude: List of entity names to exclude from processing
        include_only: If provided, only process entities in this list
        filter_fn: Optional function to filter records. Takes a JSON record and returns True/False.
    """
    if exclude is None:
        exclude = []

    if not openalex_source_path.exists():
        print(f"❌ Source directory not found: {openalex_source_path}")
        return

    print("🚀 Starting OpenAlex to Parquet conversion")
    print(f"📂 Source: {openalex_source_path}")
    print(f"📂 Destination: {parquet_destination_path}")

    # Find all entities (folders)
    all_entities = [d.name for d in openalex_source_path.iterdir() if d.is_dir()]

    # Apply filtering logic
    entities = []
    for entity in all_entities:
        # Skip if in exclude list
        if entity in exclude:
            print(f"⏭️  Excluding {entity} (in exclude list)")
            continue

        # If include_only is set, only include entities in that list
        if include_only is not None and entity not in include_only:
            print(f"⏭️  Skipping {entity} (not in include_only list)")
            continue

        entities.append(entity)

    if include_only:
        print(f"📋 Processing only: {', '.join(include_only)}")
        print(f"📋 Found entities to process: {', '.join(entities)}")
    else:
        print(f"📋 Entities found: {', '.join(entities)}")
        if exclude:
            print(f"🚫 Excluded: {', '.join(exclude)}")

    for entity in sorted(entities):
        try:
            process_entity_to_parquet(entity, filter_fn=filter_fn)
        except Exception as e:
            print(f"❌ Error processing entity {entity}: {e}")
            continue

    print("🎉 Conversion completed!")


def convert_merged_ids() -> None:
    """
    Process merged IDs from OpenAlex to identify entities that should be deleted.

    Merged entities are entities that have been consolidated into other entities.
    We need to track these to remove the merged-away entities from our dataset.

    The merged_ids folder contains CSV files with merge operations by date and entity type.
    """
    merged_ids_source_path = openalex_source_path / "merged_ids"
    merged_ids_dest_path = parquet_destination_path / "merged_ids"

    if not merged_ids_source_path.exists():
        print("⚠️  merged_ids folder not found in source path")
        return

    print("🔄 Processing merged IDs")
    os.makedirs(merged_ids_dest_path, exist_ok=True)

    # Clean up any temporary files from previous runs
    cleanup_temp_files(merged_ids_dest_path)

    # Find all entity type folders in merged_ids
    entity_folders = [d for d in merged_ids_source_path.iterdir() if d.is_dir()]

    if not entity_folders:
        print("    ℹ️  No entity folders found in merged_ids")
        return

    print(f"📋 Merge entity types found: {', '.join([f.name for f in entity_folders])}")

    for entity_folder in sorted(entity_folders):
        entity_type = entity_folder.name
        print(f"  🔄 Processing merged {entity_type}")

        dest_entity_path = merged_ids_dest_path / entity_type
        os.makedirs(dest_entity_path, exist_ok=True)

        # Find all CSV.gz files in the entity folder
        csv_files = list(entity_folder.glob("*.csv.gz"))

        if not csv_files:
            print(f"    ⚠️  No CSV files found for {entity_type}")
            continue

        # Create temporary consolidated CSV file for the entire entity
        temp_csv_file = dest_entity_path / f"{entity_type}_consolidated.csv"
        temp_parquet_file = dest_entity_path / f"{entity_type}_consolidated.parquet.tmp"
        final_parquet_file = dest_entity_path / f"{entity_type}_merged.parquet"

        # Skip if final file already exists
        if final_parquet_file.exists():
            print(f"    ⏭️  Skipping {entity_type} - consolidated file already exists")
            continue

        try:
            print(f"    📄 Consolidating {len(csv_files)} CSV files for {entity_type}")

            # Consolidate all CSV.gz files into one CSV (keeping header from first file only)
            total_record_count = 0
            header_written = False

            with open(temp_csv_file, "w", encoding="utf-8") as consolidated_csv:
                for csv_file in sorted(csv_files):
                    print(f"      📦 Processing: {csv_file.name}")

                    with gzip.open(csv_file, "rt", encoding="utf-8") as csv_reader:
                        for line_num, line in enumerate(csv_reader, 1):
                            line = line.strip()
                            if line:
                                if line_num == 1:  # Header line
                                    if not header_written:
                                        consolidated_csv.write(line + "\n")
                                        header_written = True
                                        headers = line.split(",")
                                        print(
                                            f"      📊 CSV headers: {', '.join(headers)}"
                                        )
                                    # Skip header for subsequent files
                                else:  # Data line
                                    consolidated_csv.write(line + "\n")
                                    total_record_count += 1

            if total_record_count == 0:
                print(
                    f"    ⚠️  No valid records found in any CSV files for {entity_type}"
                )
                temp_csv_file.unlink()
                continue

            # Convert consolidated CSV to Parquet using Polars
            print(
                f"    💾 Converting {total_record_count} merge records from CSV to Parquet"
            )

            lazy_df = pl.scan_csv(str(temp_csv_file))
            lazy_df.sink_parquet(str(temp_parquet_file), compression="snappy")

            # Rename to final file
            temp_parquet_file.rename(final_parquet_file)

            print(
                f"    ✅ Saved: {final_parquet_file} ({total_record_count} merge records)"
            )

            # Clean up temporary file
            temp_csv_file.unlink()
            print(f"    🗑️  Removed temporary file: {temp_csv_file.name}")

        except Exception as e:
            print(f"    ❌ Error processing {entity_type}: {e}")

            # Clean up temporary files on error
            if temp_csv_file.exists():
                temp_csv_file.unlink()
                print(f"    🗑️  Cleaned up temporary file: {temp_csv_file.name}")

            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
                print(
                    f"    🗑️  Cleaned up temporary parquet file: {temp_parquet_file.name}"
                )

            continue

    print("🎉 Merged IDs processing completed!")


def filter_works(record):
    """
    Only include works that are articles and book chapters.
    And only in English and Portuguese.
    And only in the 50th percentile of citation counts.
    And only in the fields of Engineering and Computer Science.
    """

    if "type" not in record or record["type"] not in ["article", "book-chapter"]:
        return False

    if "language" not in record or record["language"] not in ["en", "pt"]:
        return False

    if (
        "citation_normalized_percentile" not in record
        or record["citation_normalized_percentile"] is None
        or record["citation_normalized_percentile"]["value"] < 0.50
    ):
        return False

    if (
        "primary_topic" not in record
        or record["primary_topic"] is None
        or record["primary_topic"]["field"]["id"]
        not in [
            22,  # Engineering
            "https://openalex.org/fields/22",  # Engineering
            17,  # Computer Science
            "https://openalex.org/fields/17",  # Computer Science
        ]
    ):
        return False

    return True


def monitor_sink_progress(temp_parquet_file: Path, interval: int = 30) -> None:
    """
    Monitor the sink_parquet progress by checking file size growth.
    This runs in a separate thread to detect if the process is stuck.
    """

    def check_progress():
        last_size = 0
        no_progress_count = 0

        while True:
            time.sleep(interval)

            if not temp_parquet_file.exists():
                continue

            current_size = temp_parquet_file.stat().st_size

            if current_size > last_size:
                print(f"    📈 Progress: Output file size: {current_size:,} bytes")
                last_size = current_size
                no_progress_count = 0
            else:
                no_progress_count += 1
                if no_progress_count >= 3:  # 90 seconds of no progress
                    print(
                        f"    ⚠️  WARNING: No file size growth for {no_progress_count * interval}s"
                    )
                    print(f"    📏 File size stuck at: {current_size:,} bytes")

            # Exit if file is complete (will be renamed)
            if not temp_parquet_file.exists():
                break

    # Start monitoring thread
    monitor_thread = threading.Thread(target=check_progress, daemon=True)
    monitor_thread.start()
    return monitor_thread


if __name__ == "__main__":
    convert_all_entities(exclude=["works"])
    convert_all_entities(include_only=["works"], filter_fn=filter_works)
    convert_merged_ids()

# Example usage with filtering:
#
# def filter_recent_works(record):
#     """Only include works from 2020 onwards"""
#     if 'publication_year' in record:
#         return record['publication_year'] >= 2020
#     return True
#
# def filter_english_works(record):
#     """Only include works in English"""
#     if 'language' in record:
#         return record['language'] == 'en'
#     return True
#
# def filter_high_citation_works(record):
#     """Only include works with more than 10 citations"""
#     if 'cited_by_count' in record:
#         return record['cited_by_count'] > 10
#     return True
#
# # Usage examples:
# convert_all_entities(include_only=["works"], filter_fn=filter_recent_works)
# convert_all_entities(exclude=["merged_ids"], filter_fn=filter_english_works)
