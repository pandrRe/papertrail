import os
import gzip
import json
import sys
import time
import threading
from pathlib import Path
import polars as pl
from .schemas import (
    work_schema,
    author_schema,
    subfields_schema,
    publisher_schema,
    source_schema,
    funders_schema,
    institutions_schema,
)

# Enable verbose logging for Polars
# pl.Config.set_verbose(True)
pl.Config.set_streaming_chunk_size(10_000)

openalex_source_path = Path("/Volumes/T7/openalex-snapshot/data")
parquet_destination_path = Path("/Volumes/T7/openalex-parquet")

os.makedirs(parquet_destination_path, exist_ok=True)

# Entity schema mapping - maps entity names to their corresponding schemas
ENTITY_SCHEMAS = {
    "works": work_schema,
    "authors": author_schema,
    "subfields": subfields_schema,
    "publishers": publisher_schema,
    "sources": source_schema,
    "funders": funders_schema,
    "institutions": institutions_schema,
}

# Entity batch size mapping - maps entity names to their optimal batch sizes
ENTITY_BATCH_SIZES = {
    "works": 200_000,  # Works are large and complex, use smaller batches
    # All other entities default to 1M records per batch
}


def process_entity_to_parquet(
    entity_name: str, filter_fn=None, batch_size: int = None
) -> None:
    """
    Processes a specific entity (authors, topics, etc.) converting
    all .gz files to parquet files using a batch strategy.
    Creates temporary JSONL files and converts to parquet when batch size is reached.

    Args:
        entity_name: Name of the entity (authors, topics, concepts, etc.)
        filter_fn: Optional function to filter records. Takes a JSON record and returns True/False.
        batch_size: Number of records per batch before converting to parquet.
                   If None, uses entity-specific batch size or default of 1,000,000
    """
    # Determine batch size for this entity
    if batch_size is None:
        batch_size = ENTITY_BATCH_SIZES.get(entity_name, 1_000_000)

    source_entity_path = openalex_source_path / entity_name
    dest_entity_path = parquet_destination_path / entity_name

    # Create destination directory
    os.makedirs(dest_entity_path, exist_ok=True)

    if not source_entity_path.exists():
        print(f"⚠️  Folder {entity_name} not found in source path")
        return

    print(f"🔄 Processing entity: {entity_name} (batch size: {batch_size:,})")

    # Clean up any temporary files from previous failed runs
    cleanup_temp_files(dest_entity_path)

    # Find all updated_date folders
    date_folders = [
        d
        for d in source_entity_path.iterdir()
        if d.is_dir() and d.name.startswith("updated_date=")
    ]

    # Initialize batch processing variables
    batch_counter = 1
    current_batch_record_count = 0
    total_filtered_count = 0
    total_processed_count = 0
    total_parquet_files = 0

    # Initialize batch files
    current_jsonl_file = None
    current_file_handle = None

    def create_new_batch():
        """Create new batch JSONL file and return file handle"""
        nonlocal current_jsonl_file, current_file_handle, batch_counter
        current_jsonl_file = dest_entity_path / f"batch_{batch_counter:04d}.jsonl"
        print(
            f"    📄 Creating batch {batch_counter} JSONL file: {current_jsonl_file.name}"
        )
        current_file_handle = open(current_jsonl_file, "w", encoding="utf-8")
        return current_file_handle

    def convert_batch_to_parquet():
        """Convert current batch JSONL to parquet and clean up"""
        nonlocal \
            current_jsonl_file, \
            current_file_handle, \
            batch_counter, \
            current_batch_record_count, \
            total_parquet_files

        if current_file_handle:
            current_file_handle.close()
            current_file_handle = None

        if current_batch_record_count == 0:
            print(f"    ⚠️  Batch {batch_counter} is empty, skipping conversion")
            if current_jsonl_file and current_jsonl_file.exists():
                current_jsonl_file.unlink()
            return

        print(
            f"    � Converting batch {batch_counter} ({current_batch_record_count:,} records) to parquet"
        )

        # Create parquet file name
        parquet_file = dest_entity_path / f"part_{batch_counter:04d}.parquet"
        temp_parquet_file = dest_entity_path / f"part_{batch_counter:04d}.parquet.tmp"

        try:
            start_time = time.time()

            # Check if we have a predefined schema for this entity
            if entity_name in ENTITY_SCHEMAS:
                schema = ENTITY_SCHEMAS[entity_name]
                print(f"    📋 Using predefined schema for {entity_name}")
                lazy_df = pl.scan_ndjson(
                    str(current_jsonl_file),
                    schema=schema,
                    low_memory=True,
                )
            else:
                print(
                    f"    🔍 No predefined schema for {entity_name}, using schema inference"
                )
                lazy_df = pl.scan_ndjson(
                    str(current_jsonl_file),
                    infer_schema_length=10_000,
                    low_memory=True,
                )

            schema_time = time.time()
            print(f"    📊 Schema setup completed in {schema_time - start_time:.2f}s")

            # Convert to parquet
            sink_start_time = time.time()
            lazy_df.sink_parquet(
                str(temp_parquet_file),
                compression="snappy",
                row_group_size=5_000,
            )

            sink_end_time = time.time()
            total_time = sink_end_time - start_time
            sink_time = sink_end_time - sink_start_time

            # Rename temporary parquet file to final name
            temp_parquet_file.rename(parquet_file)
            total_parquet_files += 1

            print(f"    ✅ Batch {batch_counter} converted in {sink_time:.2f}s")
            print(
                f"    📏 Output: {parquet_file.name} ({parquet_file.stat().st_size:,} bytes)"
            )

            # Calculate compression ratio
            jsonl_size = current_jsonl_file.stat().st_size
            parquet_size = parquet_file.stat().st_size
            compression_ratio = jsonl_size / parquet_size
            print(f"    📦 Compression ratio: {compression_ratio:.2f}x")

            # Clean up JSONL file
            current_jsonl_file.unlink()
            print(f"    �️  Removed batch JSONL: {current_jsonl_file.name}")

        except Exception as e:
            print(f"    ❌ Error converting batch {batch_counter}: {e}")

            # Clean up temporary files on error
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            if current_jsonl_file and current_jsonl_file.exists():
                current_jsonl_file.unlink()
            raise

    try:
        if filter_fn is not None:
            print(
                "    🔍 Filter function provided - will filter records during processing"
            )

        # Create first batch
        current_file_handle = create_new_batch()

        for date_folder in sorted(date_folders):
            date_name = date_folder.name  # updated_date=2023-05-17
            print(
                f"  � Processing {date_name} (current batch: {batch_counter}, records: {current_batch_record_count:,})"
            )

            # Find all .gz files in the folder
            gz_files = list(date_folder.glob("*.gz"))

            if not gz_files:
                print(f"    ⚠️  No .gz files found in {date_name}")
                continue

            # Process all .gz files in this date folder
            for gz_file in gz_files:
                print(f"    �️ Extracting {gz_file.name}")
                with gzip.open(gz_file, "rt", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():  # Ignore empty lines
                            try:
                                # Validate JSON by parsing it
                                record = json.loads(line.strip())

                                # Apply filter function if provided
                                if filter_fn is not None:
                                    if not filter_fn(record):
                                        total_filtered_count += 1
                                        continue  # Skip this record

                                # Write to current batch
                                current_file_handle.write(line.strip() + "\n")
                                current_batch_record_count += 1
                                total_processed_count += 1

                                # Check if we've reached the batch size limit
                                if current_batch_record_count >= batch_size:
                                    print(
                                        f"    📦 Batch {batch_counter} reached {batch_size:,} records, converting to parquet..."
                                    )

                                    # Convert current batch to parquet
                                    convert_batch_to_parquet()

                                    # Start new batch
                                    batch_counter += 1
                                    current_batch_record_count = 0
                                    current_file_handle = create_new_batch()

                            except json.JSONDecodeError as e:
                                print(f"      ⚠️  Error decoding JSON: {e}")
                                continue

        # Convert the final batch if it has any records
        if current_batch_record_count > 0:
            print(
                f"    📦 Final batch {batch_counter} has {current_batch_record_count:,} records, converting to parquet..."
            )
            convert_batch_to_parquet()
        else:
            # Clean up empty final batch
            if current_file_handle:
                current_file_handle.close()
            if current_jsonl_file and current_jsonl_file.exists():
                current_jsonl_file.unlink()

        # Summary
        print(f"  ✅ Entity {entity_name} processing completed:")
        print(f"    📊 Total records processed: {total_processed_count:,}")
        if filter_fn is not None:
            print(f"    � Total records filtered out: {total_filtered_count:,}")
        print(f"    � Total parquet files created: {total_parquet_files}")
        print(
            f"    📏 Average records per file: {total_processed_count // max(total_parquet_files, 1):,}"
        )

    except Exception as e:
        print(f"    ❌ Error processing entity {entity_name}: {e}")

        # Clean up any open file handles and temporary files
        if current_file_handle:
            current_file_handle.close()

        if current_jsonl_file and current_jsonl_file.exists():
            current_jsonl_file.unlink()
            print(f"    🗑️  Cleaned up temporary JSONL file: {current_jsonl_file.name}")

        # Clean up any temporary parquet files
        for temp_parquet in dest_entity_path.glob("*.parquet.tmp"):
            temp_parquet.unlink()
            print(f"    🗑️  Cleaned up temporary parquet file: {temp_parquet.name}")

        raise


def dump_jsonl_batches(
    entity_name: str, filter_fn=None, batch_size: int = None
) -> None:
    """
    Processes a specific entity (authors, topics, etc.) dumping
    all .gz files to JSONL batch files.
    Creates larger batches across multiple date folders to improve performance.

    Args:
        entity_name: Name of the entity (authors, topics, concepts, etc.)
        filter_fn: Optional function to filter records. Takes a JSON record and returns True/False.
        batch_size: Number of records per batch before creating new batch.
                   If None, uses entity-specific batch size or default of 1,000,000
    """
    # Determine batch size for this entity
    if batch_size is None:
        batch_size = ENTITY_BATCH_SIZES.get(entity_name, 1_000_000)

    source_entity_path = openalex_source_path / entity_name
    dest_entity_path = parquet_destination_path / entity_name

    # Create destination directory
    os.makedirs(dest_entity_path, exist_ok=True)

    if not source_entity_path.exists():
        print(f"⚠️  Folder {entity_name} not found in source path")
        return

    print(f"🔄 Processing entity: {entity_name} (batch size: {batch_size:,})")

    # Clean up any temporary files from previous failed runs
    cleanup_temp_files(dest_entity_path)

    # Find all updated_date folders
    date_folders = [
        d
        for d in source_entity_path.iterdir()
        if d.is_dir() and d.name.startswith("updated_date=")
    ]

    # Initialize batch processing variables
    batch_counter = 1
    current_batch_record_count = 0
    total_filtered_count = 0
    total_processed_count = 0

    # Initialize batch files
    current_jsonl_file = None
    current_file_handle = None

    def create_new_batch():
        """Create new batch JSONL file and return file handle"""
        nonlocal current_jsonl_file, current_file_handle, batch_counter
        current_jsonl_file = dest_entity_path / f"batch_{batch_counter:04d}.jsonl"
        print(
            f"    📄 Creating batch {batch_counter} JSONL file: {current_jsonl_file.name}"
        )
        current_file_handle = open(current_jsonl_file, "w", encoding="utf-8")
        return current_file_handle

    def finalize_current_batch():
        """Finalize current batch JSONL file"""
        nonlocal \
            current_jsonl_file, \
            current_file_handle, \
            batch_counter, \
            current_batch_record_count

        if current_file_handle:
            current_file_handle.close()
            current_file_handle = None

        if current_batch_record_count == 0:
            print(f"    ⚠️  Batch {batch_counter} is empty, removing file")
            if current_jsonl_file and current_jsonl_file.exists():
                current_jsonl_file.unlink()
            return

        print(
            f"    ✅ Batch {batch_counter} finalized: {current_jsonl_file.name} ({current_batch_record_count:,} records)"
        )
        print(f"    📏 JSONL file size: {current_jsonl_file.stat().st_size:,} bytes")

    try:
        # Check if there are any date folders to process
        if not date_folders:
            print(f"    ⚠️  No date folders found for {entity_name}")
            return

        if filter_fn is not None:
            print(
                "    🔍 Filter function provided - will filter records during processing"
            )

        # Create first batch
        current_file_handle = create_new_batch()

        for date_folder in sorted(date_folders):
            date_name = date_folder.name  # updated_date=2023-05-17
            print(
                f"  📁 Processing {date_name} (current batch: {batch_counter}, records: {current_batch_record_count:,})"
            )

            # Find all .gz files in the folder
            gz_files = list(date_folder.glob("*.gz"))

            if not gz_files:
                print(f"    ⚠️  No .gz files found in {date_name}")
                continue

            # Process all .gz files in this date folder
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
                                        total_filtered_count += 1
                                        continue  # Skip this record

                                # Write to current batch
                                current_file_handle.write(line.strip() + "\n")
                                current_batch_record_count += 1
                                total_processed_count += 1

                                # Check if we've reached the batch size limit
                                if current_batch_record_count >= batch_size:
                                    print(
                                        f"    📦 Batch {batch_counter} reached {batch_size:,} records, finalizing..."
                                    )

                                    # Finalize current batch
                                    finalize_current_batch()

                                    # Start new batch
                                    batch_counter += 1
                                    current_batch_record_count = 0
                                    current_file_handle = create_new_batch()

                            except json.JSONDecodeError as e:
                                print(f"      ⚠️  Error decoding JSON: {e}")
                                continue

        # Finalize the final batch if it has any records
        if current_batch_record_count > 0:
            print(
                f"    📦 Final batch {batch_counter} has {current_batch_record_count:,} records, finalizing..."
            )
            finalize_current_batch()
        else:
            # Clean up empty final batch
            if current_file_handle:
                current_file_handle.close()
            if current_jsonl_file and current_jsonl_file.exists():
                current_jsonl_file.unlink()

        # Summary
        print(f"  ✅ Entity {entity_name} processing completed:")
        print(f"    📊 Total records processed: {total_processed_count:,}")
        if filter_fn is not None:
            print(f"    📊 Total records filtered out: {total_filtered_count:,}")
        print(f"    📦 Total batches created: {batch_counter}")

    except Exception as e:
        print(f"    ❌ Error processing entity {entity_name}: {e}")

        # Clean up any open file handles and temporary files
        if current_file_handle:
            current_file_handle.close()

        if current_jsonl_file and current_jsonl_file.exists():
            current_jsonl_file.unlink()
            print(f"    🗑️  Cleaned up temporary JSONL file: {current_jsonl_file.name}")

        raise


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
    exclude: list[str] = None,
    include_only: list[str] = None,
    filter_fn=None,
    dump_batches=False,
) -> None:
    """
    Finds all entities in the source directory and processes each one.

    Args:
        exclude: List of entity names to exclude from processing
        include_only: If provided, only process entities in this list
        filter_fn: Optional function to filter records. Takes a JSON record and returns True/False.
        dump_batches: If True, use dump_jsonl_batches instead of process_entity_to_parquet
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
            if dump_batches:
                print(f"🔄 Processing {entity} with JSONL batch dumping")
                dump_jsonl_batches(entity, filter_fn=filter_fn)
            else:
                print(f"🔄 Processing {entity} with standard processing")
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
        or record["citation_normalized_percentile"]["value"] < 0.90
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


def convert_jsonl_to_parquet(entity_name: str) -> None:
    """
    Converts JSONL files to Parquet for a specific entity.
    Scans the entity directory for .jsonl files and converts each one to .parquet.

    Args:
        entity_name: Name of the entity (authors, topics, works, etc.)
    """
    dest_entity_path = parquet_destination_path / entity_name

    if not dest_entity_path.exists():
        print(f"❌ Entity directory not found: {dest_entity_path}")
        return

    print(f"🔄 Converting JSONL files to Parquet for entity: {entity_name}")

    # Find all .jsonl files in the entity directory
    jsonl_files = list(dest_entity_path.glob("*.jsonl"))

    if not jsonl_files:
        print(f"    ⚠️  No JSONL files found in {entity_name}")
        return

    print(f"    📋 Found {len(jsonl_files)} JSONL files to convert")

    for jsonl_file in sorted(jsonl_files):
        # Determine output parquet file name
        parquet_file = jsonl_file.with_suffix(".parquet")
        temp_parquet_file = jsonl_file.with_suffix(".parquet.tmp")

        # Skip if parquet file already exists
        if parquet_file.exists():
            print(f"    ⏭️  Skipping {jsonl_file.name} - parquet already exists")
            continue

        print(f"    🔄 Converting {jsonl_file.name} to parquet")

        try:
            # Get file size and record count estimation
            file_size = jsonl_file.stat().st_size
            print(f"    📏 JSONL file size: {file_size:,} bytes")

            # Count lines for progress tracking
            with open(jsonl_file, "r", encoding="utf-8") as f:
                line_count = sum(1 for line in f if line.strip())
            print(f"    📊 Records to process: {line_count:,}")

            # System resource check
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
            except ImportError:
                print("    ℹ️  psutil not available - skipping system resource check")

            start_time = time.time()

            # Create lazy frame with schema handling
            print("    🧠 Creating lazy DataFrame...")

            # Check if we have a predefined schema for this entity
            if entity_name in ENTITY_SCHEMAS:
                schema = ENTITY_SCHEMAS[entity_name]
                print(f"    📋 Using predefined schema for {entity_name}")
                lazy_df = pl.scan_ndjson(
                    str(jsonl_file),
                    schema=schema,
                    low_memory=True,
                )
            else:
                print(
                    f"    🔍 No predefined schema for {entity_name}, using schema inference"
                )
                lazy_df = pl.scan_ndjson(
                    str(jsonl_file),
                    infer_schema_length=10_000,
                    low_memory=True,
                )

            schema_time = time.time()
            print(f"    📊 Schema setup completed in {schema_time - start_time:.2f}s")
            print(f"    💾 Writing to {temp_parquet_file.name}")

            # Start progress monitoring
            monitor_thread = monitor_sink_progress(temp_parquet_file, interval=30)

            sink_start_time = time.time()

            # Convert to parquet with conservative settings
            lazy_df.sink_parquet(
                str(temp_parquet_file),
                compression="snappy",
                row_group_size=1_000,  # Conservative row group size
            )

            sink_end_time = time.time()
            total_time = sink_end_time - start_time
            sink_time = sink_end_time - sink_start_time

            print(f"    ✅ Conversion completed in {sink_time:.2f}s")
            print(f"    📊 Total processing time: {total_time:.2f}s")
            print(
                f"    📏 Output file size: {temp_parquet_file.stat().st_size:,} bytes"
            )

            # Calculate compression ratio
            compression_ratio = file_size / temp_parquet_file.stat().st_size
            print(f"    📦 Compression ratio: {compression_ratio:.2f}x")

            # Rename temporary file to final name
            print(f"    🔄 Renaming to {parquet_file.name}")
            temp_parquet_file.rename(parquet_file)

            print(
                f"    ✅ Successfully converted: {parquet_file.name} ({line_count:,} records)"
            )

        except pl.exceptions.ComputeError as e:
            print(f"    ❌ Polars compute error: {e}")
            print(f"    📊 Record count: {line_count:,}")
            # Clean up temp file
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            continue

        except pl.exceptions.SchemaError as e:
            print(f"    ❌ Polars schema error: {e}")
            print("    💡 Try reducing infer_schema_length or check data consistency")
            # Clean up temp file
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            continue

        except MemoryError as e:
            print(f"    ❌ Memory error: {e}")
            print(
                "    💡 Consider processing smaller batches or increasing system memory"
            )
            # Clean up temp file
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            continue

        except OSError as e:
            print(f"    ❌ OS/IO error: {e}")
            print("    💿 Check disk space and permissions")
            # Clean up temp file
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            continue

        except Exception as e:
            print(f"    ❌ Unexpected error: {type(e).__name__}: {e}")
            # Clean up temp file
            if temp_parquet_file.exists():
                temp_parquet_file.unlink()
            continue

    print(f"🎉 JSONL to Parquet conversion completed for {entity_name}!")


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
    convert_all_entities(include_only=["authors"])
    # convert_all_entities(
    #     include_only=["works"], filter_fn=filter_works, dump_batches=True
    # )
    # convert_merged_ids()
    # convert_jsonl_to_parquet("works")

    # Example: Convert existing JSONL files to Parquet for a specific entity
    # convert_jsonl_to_parquet("works")
    # convert_jsonl_to_parquet("authors")

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
#
# # Convert existing JSONL batch files to Parquet:
# convert_jsonl_to_parquet("works")
