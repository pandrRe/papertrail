from pathlib import Path
import polars as pl
from ..schemas import work_schema
import glob
import re
import time

# Set streaming mode for large datasets
pl.Config.set_streaming_chunk_size(10_000)

parquet_path = Path("/Volumes/T7/openalex-parquet")
works_path = parquet_path / "works"
output_path = parquet_path / "pre-dernom" / "works"

# Create output directory
output_path.mkdir(parents=True, exist_ok=True)

print("📁 Scanning individual part files...")

# Get all part files and extract part numbers
part_files = glob.glob(str(works_path / "part_*.parquet"))
part_files.sort()

print(f"Found {len(part_files)} part files")

# Initialize timing variables
processing_times = []
start_time_total = time.time()

for i, part_file in enumerate(part_files, 1):
    # Extract part number from filename
    part_match = re.search(r"part_(\d+)\.parquet", part_file)
    if not part_match:
        continue

    part_number = part_match.group(1)
    if int(part_number) < 118:
        print(f"Skipping part_{part_number}...")
        continue
    part_start_time = time.time()
    print(f"Processing part_{part_number} ({i}/{len(part_files)})...")

    # Read the individual part file
    works_df = pl.scan_parquet(part_file, schema=work_schema, low_memory=True)

    # Transform and add part column
    works_transformed = (
        works_df.filter(
            (~pl.col("is_paratext"))
            & (pl.col("authorships").is_not_null())
            & (pl.col("authorships").list.len() > 0)
            & (pl.col("primary_topic").struct.field("id").is_not_null())
        )
        .select(
            [
                "id",
                "doi",
                "title",
                "display_name",
                "publication_date",
                "language",
                "type",
                pl.col("open_access").struct.field("oa_url").alias("oa_url"),
                "ids",
                pl.col("primary_topic").struct.field("id").alias("topic_id"),
                pl.col("citation_normalized_percentile")
                .struct.field("value")
                .alias("citation_normalized_percentile_value"),
                "cited_by_count",
                "fwci",
                pl.col("authorships")
                .list.eval(
                    pl.struct(
                        [
                            pl.element()
                            .struct.field("author_position")
                            .alias("author_position"),
                            pl.struct(
                                [
                                    pl.element()
                                    .struct.field("author")
                                    .struct.field("id")
                                    .alias("id"),
                                    pl.element()
                                    .struct.field("author")
                                    .struct.field("display_name")
                                    .alias("display_name"),
                                    pl.element()
                                    .struct.field("author")
                                    .struct.field("orcid")
                                    .alias("orcid"),
                                ]
                            ).alias("author"),
                            pl.element()
                            .struct.field("institutions")
                            .list.eval(
                                pl.struct(
                                    [
                                        pl.element().struct.field("id"),
                                        pl.element().struct.field("display_name"),
                                    ]
                                )
                            )
                            .alias("institutions"),
                        ]
                    )
                )
                .alias("authorships"),
                pl.col("authorships")
                .list.eval(pl.element().struct.field("author").struct.field("id"))
                .alias("author_id"),
                "created_date",
                "updated_date",
                pl.lit(part_number).alias("part"),
            ]
        )
        .explode("author_id")
    )

    print(f"🔗 Grouping works by author and topic for part_{part_number}...")

    # Group works by author_id and topic_id with aggregations
    works_grouped = works_transformed.group_by(["author_id", "topic_id"]).agg(
        [
            pl.struct(
                [
                    "id",
                    "doi",
                    "title",
                    "display_name",
                    "publication_date",
                    "language",
                    "type",
                    "oa_url",
                    "ids",
                    "citation_normalized_percentile_value",
                    "cited_by_count",
                    "fwci",
                    "authorships",
                    "created_date",
                    "updated_date",
                ]
            ).alias("works"),
            pl.col("cited_by_count").sum().alias("total_citations_in_topic"),
            pl.col("fwci").mean().alias("average_fwci_in_topic"),
            pl.len().alias("works_count_in_topic"),
            pl.col("publication_date").max().alias("latest_publication_date_in_topic"),
            pl.first("part").alias("part"),  # Keep the part number
        ]
    )

    print(f"💾 Writing part_{part_number} with hive partitioning...")

    # Write with hive partitioning on topic_id and part
    works_grouped.sink_parquet(
        pl.PartitionByKey(
            base_path=str(output_path), by=["topic_id", "part"], include_key=True
        ),
        compression="lz4",
        mkdir=True,
        # use_pyarrow=True,
    )

    # Calculate timing and estimates
    part_end_time = time.time()
    part_duration = part_end_time - part_start_time
    processing_times.append(part_duration)

    # Calculate average time and estimate completion
    avg_time = sum(processing_times) / len(processing_times)
    remaining_parts = len(part_files) - i
    estimated_remaining_time = remaining_parts * avg_time

    # Format time estimates
    def format_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    print(
        f"     Completed in {format_time(part_duration)} | Avg: {format_time(avg_time)} | ETA: {format_time(estimated_remaining_time)}"
    )

# Final timing summary
total_time = time.time() - start_time_total


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


print(f"✅ Successfully processed all parts and saved with hive partitioning!")
print(f"📊 Total processing time: {format_time(total_time)}")
