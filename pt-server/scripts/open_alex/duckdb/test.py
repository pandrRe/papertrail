import pathlib
import polars as pl
import duckdb

dest = pathlib.Path("/Volumes/T7/openalex-parquet/authors/test")
dest.mkdir(parents=True, exist_ok=True)

# Setup temp directory for DuckDB
tmp_dir = pathlib.Path("/Volumes/T7/duckdb_tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)


def configure_duckdb(conn):
    """Configure DuckDB settings for optimal performance."""
    conn.execute("SET preserve_insertion_order=false;")
    conn.execute(f"SET temp_directory='{tmp_dir}';")
    conn.execute("SET memory_limit='128GB';")
    conn.execute("SET max_temp_directory_size='100GB';")


def get_page_path(num: int) -> pathlib.Path:
    """Get the path to a specific parquet page file based on the given number."""
    num_str = str(num).zfill(4)
    return pathlib.Path(f"/Volumes/T7/openalex-parquet/authors/part_{num_str}.parquet")


def save_topics_parquet():
    for page_num in range(96, 106):  # 97 to 105 inclusive
        df = pl.scan_parquet(get_page_path(page_num))
        q = (
            df.select(
                pl.col("id"),
                pl.col("summary_stats").struct.field("h_index").alias("h_index"),
                pl.col("topic_share"),
            )
            .filter(pl.col("h_index") >= 4)
            .explode("topic_share")
            .select(
                pl.col("id").alias("author_id"),
                pl.col("topic_share").struct.field("id").alias("topic_id"),
                pl.col("topic_share").struct.field("value").alias("value"),
            )
            .drop_nulls()
        )
        q.sink_parquet(dest / f"author_topics_{page_num}.parquet", compression="lz4")


def import_to_duckdb():
    """Import all parquet files from dest directory into author_topics table in DuckDB."""
    duckdb_path = pathlib.Path("/Volumes/T7/openalex.duckdb")

    # Get all parquet files in dest directory
    parquet_files = list(dest.glob("*.parquet"))

    if not parquet_files:
        print("No parquet files found in destination directory")
        return

    # Connect to DuckDB
    conn = duckdb.connect(str(duckdb_path))
    configure_duckdb(conn)

    skip = [
        "author_topics_97.parquet",
        "author_topics_96.parquet",
        "author_topics_105.parquet",
        "author_topics_104.parquet",
        "author_topics_101.parquet",
        "author_topics_100.parquet",
        "author_topics_99.parquet",
        "author_topics_98.parquet",
    ]

    try:
        for parquet_file in parquet_files:
            if parquet_file.name in skip:
                print(f"Skipping {parquet_file.name} to avoid duplicates...")
                continue
            print(f"Importing {parquet_file.name}...")

            # Use DuckDB's direct parquet reading capability with INSERT OR IGNORE
            query = f"""
            INSERT OR IGNORE INTO author_topics 
            SELECT author_id, topic_id, value 
            FROM read_parquet('{parquet_file}')
            """

            conn.execute(query)
            print(f"Successfully imported {parquet_file.name}")

        print(f"Imported {len(parquet_files)} parquet files into author_topics table")

    except Exception as e:
        print(f"Error importing parquet files: {e}")
    finally:
        conn.close()


def checkpoint_database():
    """Run checkpoint on the source database to ensure all data is written to disk."""
    source_path = pathlib.Path("/Volumes/T7/openalex.duckdb")

    conn = duckdb.connect(str(source_path))
    configure_duckdb(conn)

    try:
        print("Running checkpoint on source database...")
        conn.execute("CHECKPOINT;")
        print("Checkpoint completed successfully")

    except Exception as e:
        print(f"Error running checkpoint: {e}")
    finally:
        conn.close()


def copy_duckdb():
    """Copy openalex.duckdb to openalex_copy.duckdb using ATTACH and COPY FROM DATABASE."""
    source_path = pathlib.Path("/Volumes/T7/openalex.duckdb")
    dest_path = pathlib.Path("/Volumes/T7/openalex_copy.duckdb")

    # First run checkpoint on source database
    checkpoint_database()

    # Remove destination if it exists
    if dest_path.exists():
        dest_path.unlink()
        print(f"Removed existing {dest_path.name}")

    # Connect to a temporary database to perform the copy operation
    conn = duckdb.connect()
    configure_duckdb(conn)

    try:
        print("Attaching databases...")

        # Attach source and destination databases
        conn.execute(f"ATTACH '{source_path}' AS source_db;")
        conn.execute(f"ATTACH '{dest_path}' AS dest_db;")

        print("Copying database...")

        # Copy from source to destination
        conn.execute("COPY FROM DATABASE source_db TO dest_db;")

        print(f"Successfully copied {source_path.name} to {dest_path.name}")

    except Exception as e:
        print(f"Error copying database: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # save_topics_parquet()
    # import_to_duckdb()
    copy_duckdb()
