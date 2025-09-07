from pathlib import Path
import polars as pl
import shutil

parquet_path = Path("/Volumes/T7/openalex-parquet")
authors_path = parquet_path / "pre-dernom" / "authors"

print("📁 Scanning topic partitions...")

# Find all topic_id directories
topic_dirs = [
    d for d in authors_path.iterdir() if d.is_dir() and d.name.startswith("topic_id=")
]
print(f"Found {len(topic_dirs)} topic partitions")

total_items = 0

for topic_dir in topic_dirs:
    topic_id = topic_dir.name.split("=")[1]
    print(f"Processing topic_id={topic_id}...")

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
    
    print("     Deleted all other files and folders")

print(f"✅ Successfully merged all topic partitions! Total items processed: {total_items:,}")
