from pathlib import Path
import polars as pl
from ..schemas import author_schema
import glob
import re

# Set streaming mode for large datasets
pl.Config.set_streaming_chunk_size(10_000)

parquet_path = Path("/Volumes/T7/openalex-parquet")
authors_path = parquet_path / "authors"
output_path = parquet_path / "pre-dernom" / "authors"

# Create output directory
output_path.mkdir(parents=True, exist_ok=True)

print("📁 Scanning individual part files...")

# Get all part files and extract part numbers
part_files = glob.glob(str(authors_path / "part_*.parquet"))
part_files.sort()

print(f"Found {len(part_files)} part files")

for part_file in part_files:
    # Extract part number from filename
    part_match = re.search(r"part_(\d+)\.parquet", part_file)
    if not part_match:
        continue

    part_number = part_match.group(1)
    print(f"Processing part_{part_number}...")

    # Read the individual part file
    authors_df = pl.scan_parquet(part_file, schema=author_schema, low_memory=True)

    # Transform and add part column
    authors_transformed_raw = authors_df.filter(
        (pl.col("cited_by_count") > 0)
        & (pl.col("summary_stats").struct.field("h_index") >= 4)
        & (pl.col("topic_share").list.len() > 0)
    ).select(
        [
            "id",
            "orcid",
            "display_name",
            "display_name_alternatives",
            "works_count",
            "cited_by_count",
            "summary_stats",
            "ids",
            pl.col("last_known_institutions")
            .list.eval(
                pl.struct(
                    [
                        pl.element().struct.field("id"),
                        pl.element().struct.field("display_name"),
                        pl.element().struct.field("country_code"),
                    ]
                )
            )
            .alias("latest_institutions"),
            pl.col("topic_share")
            .list.eval(
                pl.struct(
                    [
                        pl.element().struct.field("id"),
                        pl.element().struct.field("value"),
                    ]
                )
            )
            .alias("topics"),
            pl.lit(part_number).alias("part"),
        ]
    )

    # Explode topics and transform structure
    authors_exploded = (
        authors_transformed_raw.explode("topics")
        .with_columns(
            [
                pl.col("id").alias("author_id"),
                pl.col("topics").struct.field("id").alias("topic_id"),
                pl.col("topics").struct.field("value").alias("topic_share_value"),
            ]
        )
        .drop(["id", "topics"])
    )

    print(f"💾 Writing part_{part_number} with hive partitioning...")

    # Write with hive partitioning on topic_id
    authors_exploded.sink_parquet(
        pl.PartitionByKey(
            base_path=str(output_path), by=["topic_id", "part"], include_key=True
        ),
        compression="lz4",
        mkdir=True,
    )

print("✅ Successfully processed all parts and saved with hive partitioning!")
