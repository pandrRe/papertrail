from pathlib import Path
import polars as pl
import shutil
import time

parquet_path = Path("/Volumes/T7/openalex-parquet")
works_path = parquet_path / "pre-dernom" / "works"

print("📁 Scanning works topic partitions...")

# Find all topic_id directories
topic_dirs = [
    d for d in works_path.iterdir() if d.is_dir() and d.name.startswith("topic_id=")
]
print(f"Found {len(topic_dirs)} topic partitions")

# Initialize timing variables
total_items = 0
processing_times = []
start_time_total = time.time()


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


for i, topic_dir in enumerate(topic_dirs, 1):
    topic_id = topic_dir.name.split("=")[1]
    topic_start_time = time.time()
    print(f"Processing topic_id={topic_id} ({i}/{len(topic_dirs)})...")

    merged_topic_df = pl.read_parquet(topic_dir / "**/*.parquet")
    df_len = len(merged_topic_df)
    total_items += df_len

    output_file = topic_dir / "0.parquet"
    merged_topic_df.write_parquet(str(output_file), compression="lz4")

    print(f"     Merged all files into 0.parquet ({df_len:,} items)")

    # Delete all other files and subdirectories, keeping only 0.parquet
    for item in topic_dir.iterdir():
        if item.name != "0.parquet":
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    # Calculate timing and estimates
    topic_end_time = time.time()
    topic_duration = topic_end_time - topic_start_time
    processing_times.append(topic_duration)

    # Calculate average time and estimate completion
    avg_time = sum(processing_times) / len(processing_times)
    remaining_topics = len(topic_dirs) - i
    estimated_remaining_time = remaining_topics * avg_time

    print(
        f"     Completed in {format_time(topic_duration)} | Avg: {format_time(avg_time)} | ETA: {format_time(estimated_remaining_time)}"
    )
    print("     Deleted all other files and folders")

# Final timing summary
total_time = time.time() - start_time_total

print(
    f"✅ Successfully merged all topic partitions! Total items processed: {total_items:,}"
)
print(f"📊 Total processing time: {format_time(total_time)}")
print(
    f"📊 Average time per topic: {format_time(sum(processing_times) / len(processing_times))}"
)
