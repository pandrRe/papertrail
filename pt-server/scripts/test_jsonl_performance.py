#!/usr/bin/env python3
"""
Test script to benchmark Polars scan_ndjson performance on real JSONL files.

This script tests different configurations and scenarios for processing
JSONL files with Polars, particularly useful for OpenAlex dataset processing.

Usage:
    python test_jsonl_performance.py [path_to_jsonl_file]

Example:
    python test_jsonl_performance.py /Volumes/T7/openalex-parquet/works/test.jsonl
"""

import os
import sys
import time
import threading
from pathlib import Path
import polars as pl
import json
import gzip

# Enable verbose logging for Polars
pl.Config.set_verbose(True)


def monitor_memory_usage(interval: int = 10, duration: int = 300):
    """
    Monitor memory usage during processing.
    
    Args:
        interval: How often to check memory (seconds)
        duration: How long to monitor (seconds)
    """
    def check_memory():
        try:
            import psutil
            process = psutil.Process()
            start_time = time.time()
            
            while time.time() - start_time < duration:
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                
                print(f"    🧠 Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB ({memory_percent:.1f}%)")
                
                # System memory
                sys_memory = psutil.virtual_memory()
                print(f"    💾 System memory: {sys_memory.percent:.1f}% used, {sys_memory.available / 1024 / 1024 / 1024:.1f} GB available")
                
                time.sleep(interval)
                
        except ImportError:
            print("    ℹ️  psutil not available - skipping memory monitoring")
            return
        except Exception as e:
            print(f"    ⚠️  Memory monitoring error: {e}")
            return
    
    monitor_thread = threading.Thread(target=check_memory, daemon=True)
    monitor_thread.start()
    return monitor_thread


def test_file_info(file_path: Path):
    """Display basic information about the test file."""
    print(f"📁 Test file: {file_path}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    file_size = file_path.stat().st_size
    print(f"📏 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
    
    # Count lines in file
    print("🔢 Counting lines in file...")
    line_count = 0
    
    try:
        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for _ in f:
                    line_count += 1
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in f:
                    line_count += 1
        
        print(f"📊 Total lines: {line_count:,}")
        
        # Sample first few records
        print("🔍 Sample records:")
        sample_count = 0
        
        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    if sample_count >= 3:
                        break
                    try:
                        record = json.loads(line.strip())
                        print(f"    Record {sample_count + 1}: {len(record)} fields")
                        if 'id' in record:
                            print(f"      ID: {record['id']}")
                        if 'type' in record:
                            print(f"      Type: {record['type']}")
                        sample_count += 1
                    except json.JSONDecodeError:
                        continue
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if sample_count >= 3:
                        break
                    try:
                        record = json.loads(line.strip())
                        print(f"    Record {sample_count + 1}: {len(record)} fields")
                        if 'id' in record:
                            print(f"      ID: {record['id']}")
                        if 'type' in record:
                            print(f"      Type: {record['type']}")
                        sample_count += 1
                    except json.JSONDecodeError:
                        continue
        
    except Exception as e:
        print(f"⚠️  Error analyzing file: {e}")
        return False
    
    return True


def test_scan_ndjson_basic(file_path: Path):
    """Test basic scan_ndjson functionality."""
    print("\n🧪 Test 1: Basic scan_ndjson")
    print("=" * 50)
    
    try:
        start_time = time.time()
        
        print("📊 Creating lazy DataFrame...")
        lazy_df = pl.scan_ndjson(str(file_path))
        
        schema_time = time.time()
        print(f"✅ Lazy DataFrame created in {schema_time - start_time:.2f}s")
        
        # Try to get basic info
        print("📋 Getting schema...")
        try:
            schema = lazy_df.schema
            print(f"📊 Schema has {len(schema)} columns")
            print("📝 First 10 columns:")
            for i, (col_name, col_type) in enumerate(list(schema.items())[:10]):
                print(f"    {i+1}. {col_name}: {col_type}")
        except Exception as e:
            print(f"⚠️  Could not get schema: {e}")
        
        # Try to count rows (this forces some execution)
        print("🔢 Counting rows...")
        count_start = time.time()
        
        try:
            row_count = lazy_df.select(pl.count()).collect().item()
            count_time = time.time()
            print(f"📊 Row count: {row_count:,}")
            print(f"⏱️  Count operation took {count_time - count_start:.2f}s")
        except Exception as e:
            print(f"❌ Error counting rows: {e}")
            return False
        
        total_time = time.time() - start_time
        print(f"✅ Basic test completed in {total_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def test_scan_ndjson_with_settings(file_path: Path):
    """Test scan_ndjson with different settings."""
    print("\n🧪 Test 2: scan_ndjson with conservative settings")
    print("=" * 50)
    
    settings_to_test = [
        {
            "name": "Conservative",
            "params": {
                "infer_schema_length": 1_000,
                "low_memory": True
            }
        },
        {
            "name": "Moderate", 
            "params": {
                "infer_schema_length": 10_000,
                "low_memory": True
            }
        },
        {
            "name": "Aggressive",
            "params": {
                "infer_schema_length": 100_000,
                "low_memory": False
            }
        }
    ]
    
    for setting in settings_to_test:
        print(f"\n📊 Testing {setting['name']} settings:")
        print(f"    Parameters: {setting['params']}")
        
        try:
            start_time = time.time()
            
            lazy_df = pl.scan_ndjson(str(file_path), **setting['params'])
            
            schema_time = time.time()
            print(f"    ✅ Lazy DataFrame created in {schema_time - start_time:.2f}s")
            
            # Try a simple operation
            try:
                head_result = lazy_df.head(100).collect()
                collect_time = time.time()
                print(f"    📊 Collected 100 rows in {collect_time - schema_time:.2f}s")
                print(f"    📋 Actual rows collected: {len(head_result)}")
                
            except Exception as e:
                print(f"    ⚠️  Could not collect sample: {e}")
                
        except Exception as e:
            print(f"    ❌ {setting['name']} settings failed: {e}")


def test_streaming_operations(file_path: Path):
    """Test streaming operations on the JSONL file."""
    print("\n🧪 Test 3: Streaming operations")
    print("=" * 50)
    
    try:
        print("📊 Setting up streaming pipeline...")
        
        # Start memory monitoring
        memory_monitor = monitor_memory_usage(interval=15, duration=300)
        
        start_time = time.time()
        
        lazy_df = pl.scan_ndjson(
            str(file_path),
            infer_schema_length=10_000,
            low_memory=True
        )
        
        # Create a streaming pipeline with some operations
        print("🔄 Building streaming pipeline...")
        pipeline = (
            lazy_df
            .with_row_index()  # Add row numbers
            .filter(pl.col("id").is_not_null())  # Filter out rows without ID
        )
        
        # Try to sink to a temporary parquet file
        temp_output = file_path.parent / "test_output.parquet.tmp"
        
        print(f"💾 Streaming to temporary parquet: {temp_output}")
        print("⏱️  This may take a while...")
        
        sink_start = time.time()
        
        pipeline.sink_parquet(
            str(temp_output),
            compression="snappy",
            row_group_size=5_000,
            statistics=False
        )
        
        sink_end = time.time()
        
        if temp_output.exists():
            output_size = temp_output.stat().st_size
            print(f"✅ Streaming completed in {sink_end - sink_start:.2f}s")
            print(f"📏 Output size: {output_size:,} bytes ({output_size / 1024 / 1024:.1f} MB)")
            
            # Clean up
            temp_output.unlink()
            print("🗑️  Cleaned up temporary file")
        else:
            print("❌ Output file was not created")
            
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        
        # Clean up on error
        temp_output = file_path.parent / "test_output.parquet.tmp"
        if temp_output.exists():
            temp_output.unlink()
            print("🗑️  Cleaned up temporary file after error")


def test_memory_limits(file_path: Path):
    """Test behavior under memory constraints."""
    print("\n🧪 Test 4: Memory limit behavior")
    print("=" * 50)
    
    try:
        import psutil
        
        # Get current memory info
        memory = psutil.virtual_memory()
        available_gb = memory.available / 1024 / 1024 / 1024
        
        print(f"💾 Available memory: {available_gb:.1f} GB")
        
        if available_gb < 2:
            print("⚠️  Low memory detected - testing conservative settings only")
            
            lazy_df = pl.scan_ndjson(
                str(file_path),
                infer_schema_length=500,
                low_memory=True
            )
            
            # Try small operations only
            result = lazy_df.head(10).collect()
            print(f"✅ Successfully processed {len(result)} rows with low memory")
            
        else:
            print("🧠 Sufficient memory - testing various batch sizes")
            
            batch_sizes = [1_000, 5_000, 10_000]
            
            for batch_size in batch_sizes:
                print(f"📊 Testing batch size: {batch_size:,}")
                
                try:
                    start_time = time.time()
                    
                    lazy_df = pl.scan_ndjson(
                        str(file_path),
                        infer_schema_length=batch_size,
                        low_memory=True
                    )
                    
                    # Process a sample
                    sample = lazy_df.head(1000).collect()
                    
                    end_time = time.time()
                    print(f"    ✅ Processed {len(sample)} rows in {end_time - start_time:.2f}s")
                    
                except Exception as e:
                    print(f"    ❌ Failed with batch size {batch_size}: {e}")
                    
    except ImportError:
        print("ℹ️  psutil not available - skipping memory limit tests")
    except Exception as e:
        print(f"❌ Memory limit test failed: {e}")


def run_performance_benchmark(file_path: Path):
    """Run a comprehensive performance benchmark."""
    print("\n🏁 Performance Benchmark")
    print("=" * 60)
    
    # System info
    try:
        import psutil
        
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        
        print(f"🖥️  CPU cores: {cpu_count}")
        print(f"💾 Total RAM: {memory.total / 1024 / 1024 / 1024:.1f} GB")
        print(f"💾 Available RAM: {memory.available / 1024 / 1024 / 1024:.1f} GB")
        
    except ImportError:
        print("ℹ️  System info not available (psutil not installed)")
    
    # File info
    file_size_mb = file_path.stat().st_size / 1024 / 1024
    print(f"📁 File size: {file_size_mb:.1f} MB")
    
    # Run all tests
    print("\n🚀 Starting benchmark tests...")
    
    results = {
        "basic": test_scan_ndjson_basic(file_path),
        "settings": test_scan_ndjson_with_settings(file_path),
        "streaming": test_streaming_operations(file_path),
        "memory": test_memory_limits(file_path)
    }
    
    # Summary
    print("\n📋 Test Results Summary:")
    print("=" * 30)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.capitalize():12} {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nOverall success rate: {success_rate:.0f}%")


def main():
    """Main function to run the benchmark."""
    print("🧪 Polars scan_ndjson Performance Test")
    print("=" * 40)
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # Default test file locations
        default_paths = [
            Path("/Volumes/T7/openalex-parquet/works/test.jsonl"),
            Path("/Volumes/T7/openalex-snapshot/data/works/updated_date=2024-01-01/part_000.gz"),
            Path("./test.jsonl")
        ]
        
        file_path = None
        for path in default_paths:
            if path.exists():
                file_path = path
                break
        
        if file_path is None:
            print("❌ No test file found. Please provide a path:")
            print("Usage: python test_jsonl_performance.py <path_to_jsonl_file>")
            print("\nLooking for files in these locations:")
            for path in default_paths:
                print(f"  - {path}")
            return 1
    
    # Validate and analyze the test file
    if not test_file_info(file_path):
        print("❌ Cannot proceed with invalid test file")
        return 1
    
    # Run the benchmark
    try:
        run_performance_benchmark(file_path)
        print("\n🎉 Benchmark completed!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


# Additional utility functions for specific testing scenarios

def create_test_jsonl(output_path: Path, num_records: int = 10000):
    """
    Create a test JSONL file with sample OpenAlex-like records.
    
    Args:
        output_path: Where to save the test file
        num_records: Number of records to generate
    """
    print(f"📝 Creating test JSONL file with {num_records:,} records...")
    
    import random
    import string
    
    def random_string(length: int = 10) -> str:
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(num_records):
            record = {
                "id": f"https://openalex.org/W{random.randint(1000000000, 9999999999)}",
                "title": f"Test Article {i+1}: {random_string(20)}",
                "type": random.choice(["article", "book-chapter", "preprint"]),
                "publication_year": random.randint(2000, 2024),
                "cited_by_count": random.randint(0, 1000),
                "language": random.choice(["en", "pt", "es", "fr"]),
                "abstract": random_string(200),
                "authors": [
                    {
                        "id": f"https://openalex.org/A{random.randint(1000000, 9999999)}",
                        "display_name": f"Author {random_string(8)}"
                    } for _ in range(random.randint(1, 5))
                ]
            }
            
            f.write(json.dumps(record) + '\n')
    
    print(f"✅ Test file created: {output_path}")
    return output_path


def test_with_sample_data():
    """Create and test with a sample dataset."""
    test_file = Path("./sample_test.jsonl")
    
    try:
        create_test_jsonl(test_file, num_records=5000)
        run_performance_benchmark(test_file)
        
    finally:
        if test_file.exists():
            test_file.unlink()
            print("🗑️  Cleaned up test file")
