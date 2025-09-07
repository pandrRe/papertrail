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

# Create output directory
output_path = parquet_path / "denormalized"
output_path.mkdir(parents=True, exist_ok=True)

print(f"🚀 Processing {len(common_topic_ids)} common topics...")

start_time_total = time.time()
processing_times = []
total_records = 0

for i, topic_id in enumerate(sorted(common_topic_ids), 1):
    topic_start_time = time.time()
    print(f"\n📂 Processing topic_id={topic_id} ({i}/{len(common_topic_ids)})...")
    
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
    authors_df = pl.read_parquet(str(authors_file))
    works_df = pl.read_parquet(str(works_file))
    
    # Drop duplicate combinations
    authors_df = authors_df.unique(subset=["author_id", "topic_id"])
    works_df = works_df.unique(subset=["author_id", "topic_id"])
    
    # Perform inner join
    joined_df = authors_df.join(works_df, on=["author_id", "topic_id"], how="inner")
    joined_count = len(joined_df)
    
    if joined_count > 0:
        # Write denormalized data to topic partition
        topic_output_dir = output_path / f"topic_id={topic_id}"
        topic_output_dir.mkdir(parents=True, exist_ok=True)
        
        joined_df.write_parquet(
            str(topic_output_dir / "0.parquet"),
            compression="lz4"
        )
        
        total_records += joined_count
        print(f"   ✅ Wrote {joined_count:,} records")
    else:
        print(f"   ⚠️  No matching records found - skipping")
    
    # Calculate timing and estimates
    topic_end_time = time.time()
    topic_duration = topic_end_time - topic_start_time
    processing_times.append(topic_duration)
    
    # Calculate average time and estimate completion
    avg_time = sum(processing_times) / len(processing_times)
    remaining_topics = len(common_topic_ids) - i
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
    
    print(f"   ⏱️  {format_time(topic_duration)} | Avg: {format_time(avg_time)} | ETA: {format_time(estimated_remaining_time)}")

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
