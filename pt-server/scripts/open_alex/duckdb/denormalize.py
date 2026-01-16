from pathlib import Path
import polars as pl
import time

# Set up paths
parquet_path = Path("/Volumes/T7/openalex-parquet")
authors_path = parquet_path / "pre-dernom" / "authors"
works_path = parquet_path / "pre-dernom" / "works"

print("📁 Scanning topic partitions...")

# Find all topic_id directories in authors and works
authors_topics = [
    d for d in authors_path.iterdir() if d.is_dir() and d.name.startswith("topic_id=")
]
works_topics = [
    d for d in works_path.iterdir() if d.is_dir() and d.name.startswith("topic_id=")
]

print(f"Found {len(authors_topics)} author topic partitions")
print(f"Found {len(works_topics)} works topic partitions")

# Find common topics
authors_topic_ids = {d.name.split("=")[1] for d in authors_topics}
works_topic_ids = {d.name.split("=")[1] for d in works_topics}
common_topic_ids = authors_topic_ids.intersection(works_topic_ids)

print(f"Common topics: {len(common_topic_ids)}")

if not common_topic_ids:
    print("❌ No common topics found between authors and works!")
    exit(1)

# Sort topics by works file size (ascending - smallest first)
print("📏 Sorting topics by file size...")
topic_sizes = []
for topic_id in common_topic_ids:
    works_file = works_path / f"topic_id={topic_id}" / "0.parquet"
    if works_file.exists():
        file_size = works_file.stat().st_size
        topic_sizes.append((topic_id, file_size))

# Sort by file size (ascending)
topic_sizes.sort(key=lambda x: x[1])
sorted_topic_ids = [topic_id for topic_id, _ in topic_sizes]

print(
    f"📊 Topic size range: {topic_sizes[0][1]:,} bytes (smallest) to {topic_sizes[-1][1]:,} bytes (largest)"
)

# Create output directory
output_path = parquet_path / "denormalized-v2"
output_path.mkdir(parents=True, exist_ok=True)

print(f"🚀 Processing {len(sorted_topic_ids)} common topics (smallest to largest)...")

start_time_total = time.time()
processing_times = []
total_records = 0

for i, topic_id in enumerate(sorted_topic_ids, 1):
    topic_start_time = time.time()
    print(f"\n📂 Processing topic_id={topic_id} ({i}/{len(sorted_topic_ids)})...")

    # Check if topic already exists in output
    topic_output_dir = output_path / f"topic_id={topic_id}"
    if topic_output_dir.exists() and (topic_output_dir / "0.parquet").exists():
        print(f"   ⏭️  Topic already processed - skipping")
        continue

    # Load authors data for this topic
    authors_topic_dir = authors_path / f"topic_id={topic_id}"
    authors_file = authors_topic_dir / "0.parquet"

    if not authors_file.exists():
        print(f"⚠️  Authors file not found: {authors_file} - skipping")
        continue

    # Load works data for this topic
    works_topic_dir = works_path / f"topic_id={topic_id}"
    works_file = works_topic_dir / "0.parquet"

    if not works_file.exists():
        print(f"⚠️  Works file not found: {works_file} - skipping")
        continue

    # Load data
    authors_df = pl.scan_parquet(str(authors_file), low_memory=True)
    works_df = pl.scan_parquet(str(works_file), low_memory=True)

    # Drop duplicate combinations for authors
    authors_df = authors_df.unique(subset=["author_id", "topic_id"])

    # For works, group by topic_id and author_id, aggregating the other fields properly
    works_df = works_df.group_by(["topic_id", "author_id"]).agg(
        [
            pl.col("works").flatten().alias("works"),
            pl.col("total_citations_in_topic").sum().alias("total_citations_in_topic"),
            pl.col("average_fwci_in_topic").mean().alias("average_fwci_in_topic"),
            pl.col("works_count_in_topic").sum().alias("works_count_in_topic"),
            pl.col("latest_publication_date_in_topic")
            .max()
            .alias("latest_publication_date_in_topic"),
        ]
    )

    # Perform inner join
    joined_df = authors_df.join(works_df, on=["author_id", "topic_id"], how="inner")

    # Write denormalized data to topic partition (topic_output_dir already defined above)
    topic_output_dir.mkdir(parents=True, exist_ok=True)

    # Write to temporary file first
    temp_file = topic_output_dir / "0.parquet.tmp"
    final_file = topic_output_dir / "0.parquet"

    joined_df.sink_parquet(str(temp_file), compression="lz4")

    # Rename to final file after successful write
    temp_file.rename(final_file)

    # Read the final file to get the actual record count
    joined_count = len(pl.read_parquet(str(final_file)))
    total_records += joined_count
    print(f"   ✅ Wrote {joined_count:,} records")

    # Calculate timing and estimates
    topic_end_time = time.time()
    topic_duration = topic_end_time - topic_start_time
    processing_times.append(topic_duration)

    # Calculate average time and estimate completion
    avg_time = sum(processing_times) / len(processing_times)
    remaining_topics = len(sorted_topic_ids) - i
    estimated_remaining_time = remaining_topics * avg_time

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
        f"   ⏱️  {format_time(topic_duration)} | Avg: {format_time(avg_time)} | ETA: {format_time(estimated_remaining_time)}"
    )

# Final summary
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


print(f"\n✅ Successfully processed all topics!")
print(f"📊 Total records written: {total_records:,}")
print(f"⏱️  Total processing time: {format_time(total_time)}")
print(f"📁 Output location: {output_path}")
