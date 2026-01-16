from pathlib import Path
import polars as pl

# Set up paths
parquet_path = Path("/Volumes/T7/openalex-parquet")
# denormalized_path = parquet_path / "denormalized"
denormalized_path = parquet_path / "pre-dernom" / "works"

print("📁 Scanning denormalized topic partitions...")

# Find all topic_id directories
topic_dirs = [
    d
    for d in denormalized_path.iterdir()
    if d.is_dir() and d.name.startswith("topic_id=")
]

print(f"Found {len(topic_dirs)} denormalized topic partitions")

if not topic_dirs:
    print("❌ No denormalized partitions found!")
    exit(1)

# Use the first topic partition to inspect schema
first_topic_dir = topic_dirs[0]
topic_id = first_topic_dir.name.split("=")[1]
parquet_file = first_topic_dir / "0.parquet"

if not parquet_file.exists():
    print(f"❌ Parquet file not found: {parquet_file}")
    exit(1)

print(f"\n🔍 Inspecting schema from topic_id={topic_id}")
print(f"📄 File: {parquet_file}")

# Read the parquet file and get schema
df = pl.read_parquet(str(parquet_file))

print(f"\n📊 Dataset Info:")
print(f"Records: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print(f"\n📋 Schema:")
print(df.schema)

print(f"\n📋 Detailed Column Info:")
for i, (col_name, col_type) in enumerate(df.schema.items(), 1):
    print(f"{i:2d}. {col_name:<35} {col_type}")

print(f"\n📋 Sample Data (first 3 rows):")
print(df.head(3))

# Check if we can read all partitions at once
print(f"\n🔍 Testing reading all partitions...")
try:
    all_df = pl.read_parquet(str(denormalized_path / "**/*.parquet"))
    total_records = len(all_df)
    print(f"✅ Successfully read all partitions: {total_records:,} total records")

    # Show distribution by topic
    topic_counts = (
        all_df.group_by("topic_id")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
    )
    print(f"\n📊 Top 10 topics by record count:")
    print(topic_counts.head(10))

except Exception as e:
    print(f"⚠️  Could not read all partitions: {e}")
    print("Individual topic files are available for processing")
