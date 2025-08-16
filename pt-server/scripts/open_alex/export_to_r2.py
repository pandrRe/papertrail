import polars as pl
from pathlib import Path
from typing import Optional
from .schemas import (
    author_schema,
    subfields_schema,
    publisher_schema,
    source_schema,
    funders_schema,
)  # Importing schemas from schemas module


# Configure Polars
pl.Config.set_verbose(True)
pl.Config.set_streaming_chunk_size(10_000)

# Path configuration (from open_alex_parquet.py)
parquet_destination_path = Path("/Volumes/T7/openalex-parquet")


def fix_funders_frame(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Fix extra column 'country_id' in funders entity.
    """
    # Use scan with extra_columns='ignore' approach by recreating the scan
    try:
        return df.drop("country_id")
    except Exception:
        # If column doesn't exist or other error, return as-is
        return df


def fix_institutions_frame(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Fix extra column 'country_id' in institutions entity.
    """
    try:
        return df.drop("country_id")
    except Exception:
        # If column doesn't exist or other error, return as-is
        return df


def fix_sources_frame(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Fix extra column 'topic_share' in sources entity.
    """
    try:
        return df.drop("topic_share")
    except Exception:
        # If column doesn't exist or other error, return as-is
        return df


def fix_subfields_frame(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Fix data type mismatch for column display_name_alternatives in subfields entity.
    The error indicates String incoming but Null expected.
    """
    return df.with_columns(
        [
            # Cast display_name_alternatives to handle String values
            # pl.when(pl.col("display_name_alternatives").is_null())
            # .then(pl.col("display_name_alternatives"))
            # .otherwise(pl.col("display_name_alternatives").cast(pl.List(pl.Utf8)))
            # .alias("display_name_alternatives")
            pl.col("display_name_alternatives")
            .cast(pl.List(pl.Utf8))
            .alias("display_name_alternatives")
        ]
    )


# Dictionary mapping entity names to their fix functions
ENTITY_FIXES = {
    # "funders": fix_funders_frame,
    # "institutions": fix_institutions_frame,
    # "sources": fix_sources_frame,
    # "subfields": fix_subfields_frame,
}

# Dictionary mapping entity names to custom scan_parquet arguments
ENTITY_CUSTOM_ARGUMENTS = {
    "authors": {
        "schema": author_schema,
        "low_memory": True,  # Enable low memory mode for authors
        "extra_columns": "ignore",  # Ignore extra columns
    },
    # "publishers": {
    #     "schema": publisher_schema,
    #     "cast_options": pl.ScanCastOptions(missing_struct_fields="insert"),
    # },
    # "subfields": {"schema": subfields_schema, "extra_columns": "ignore"},
    # "concepts": {"cast_options": pl.ScanCastOptions(missing_struct_fields="insert")},
    # "sources": {"schema": source_schema, "extra_columns": "ignore"},
    # "funders": {"schema": funders_schema, "extra_columns": "ignore"},
    # "institutions": {"extra_columns": "ignore"},
}


def scan_entity(entity_name: str) -> Optional[pl.LazyFrame]:
    """
    Scans all parquet files for a given entity and returns a unified LazyFrame.
    Applies manual fixes for known schema issues.

    Args:
        entity_name: Name of the entity (works, authors, topics, etc.)

    Returns:
        A Polars LazyFrame containing all records from the entity's parquet files,
        or None if the entity folder doesn't exist or has no parquet files.
    """
    entity_path = parquet_destination_path / entity_name

    if not entity_path.exists():
        print(f"❌ Entity folder not found: {entity_path}")
        return None

    # Find all parquet files in the entity folder
    parquet_files = list(entity_path.glob("*.parquet"))

    if not parquet_files:
        print(f"⚠️  No parquet files found in {entity_name}")
        return None

    print(f"📊 Found {len(parquet_files)} parquet files for entity '{entity_name}'")

    try:
        # Use scan_parquet with glob pattern for efficient lazy loading
        parquet_pattern = str(entity_path / "*.parquet")

        # Get custom arguments for this entity if they exist
        scan_kwargs = {}
        if entity_name in ENTITY_CUSTOM_ARGUMENTS:
            scan_kwargs.update(ENTITY_CUSTOM_ARGUMENTS[entity_name])
            print(
                f"🔧 Using custom scan arguments for entity '{entity_name}': {list(scan_kwargs.keys())}"
            )

        lazy_df = pl.scan_parquet(parquet_pattern, **scan_kwargs)

        # Apply manual fixes if available for this entity
        if entity_name in ENTITY_FIXES:
            print(f"🔧 Applying manual fix for entity '{entity_name}'")
            lazy_df = ENTITY_FIXES[entity_name](lazy_df)

        # Get basic info about the scan
        print(f"✅ Successfully scanned entity '{entity_name}'")

        return lazy_df

    except Exception as e:
        print(f"❌ Error scanning entity '{entity_name}': {e}")
        return None


def inspect_df(
    df: pl.LazyFrame, entity_name: str = "DataFrame", n_rows: int = 5
) -> None:
    """
    Pretty-prints the schema and head of a Polars DataFrame/LazyFrame.

    Args:
        df: Polars LazyFrame or DataFrame to inspect
        entity_name: Name of the entity for display purposes
        n_rows: Number of rows to show in head (default: 5)
    """
    if df is None:
        print(f"❌ Cannot inspect {entity_name}: DataFrame is None")
        return

    print(f"\n{'='*60}")
    print(f"🔍 INSPECTING: {entity_name.upper()}")
    print(f"{'='*60}")

    try:
        # Convert to DataFrame for inspection (collect a small sample)
        sample_df = df.limit(n_rows).collect()

        # Get basic statistics
        total_rows = df.select(pl.len()).collect().item()
        n_columns = len(sample_df.columns)

        print(f"📏 Dimensions: {total_rows:,} rows × {n_columns} columns")
        print(f"💾 Memory usage: ~{sample_df.estimated_size('mb'):.2f} MB (sample)")

        # Schema information
        print("\n📋 SCHEMA:")
        print("-" * 40)
        schema = sample_df.schema
        for i, (col_name, dtype) in enumerate(schema.items(), 1):
            print(f"{i:2d}. {col_name:<30} {dtype}")

        # Head preview
        print(f"\n👀 HEAD ({n_rows} rows):")
        print("-" * 60)
        print(sample_df)

    except Exception as e:
        print(f"❌ Error inspecting {entity_name}: {e}")
        # Try to get basic info without collecting
        try:
            schema = df.schema
            print(f"📋 Schema (lazy): {len(schema)} columns")
            for col_name, dtype in list(schema.items())[:10]:  # Show first 10 columns
                print(f"  - {col_name}: {dtype}")
            if len(schema) > 10:
                print(f"  ... and {len(schema) - 10} more columns")
        except Exception as e2:
            print(f"❌ Could not retrieve schema: {e2}")

    print(f"{'='*60}\n")


def inspect_subfields_schema():
    """
    Simple function to scan subfields parquet files and show the actual schema.
    """
    print("🔍 Scanning subfields schema...")

    entity_path = parquet_destination_path / "publishers"
    parquet_pattern = str(entity_path / "*.parquet")

    # Scan without any schema restrictions
    lazy_df = pl.scan_parquet(parquet_pattern)
    schema = lazy_df.collect_schema()

    print(f"\nSubfields Schema ({len(schema)} columns):")
    print("-" * 60)
    for i, (col_name, dtype) in enumerate(schema.items(), 1):
        print(f"{i:2d}. {col_name:<35} {dtype}")
    print("-" * 60)

    print(lazy_df.collect().head())  # Show first 5 rows for quick inspection


def get_available_entities() -> list[str]:
    """
    Returns a list of available entity names in the parquet destination path.

    Returns:
        List of entity folder names that contain parquet files
    """
    if not parquet_destination_path.exists():
        print(f"❌ Parquet destination path not found: {parquet_destination_path}")
        return []

    entities = []
    for entity_path in parquet_destination_path.iterdir():
        if entity_path.is_dir():
            # Check if folder contains parquet files
            parquet_files = list(entity_path.glob("*.parquet"))
            if parquet_files:
                entities.append(entity_path.name)

    return sorted(entities)


def inspect_all_entities(output_file: str = "openalex_entities_inspection.md"):
    """
    Main function that scans and inspects all available entities and saves results to markdown.

    Args:
        output_file: Name of the markdown file to save the inspection results
    """
    # Create output file path
    output_path = Path(output_file)

    # Open file for writing
    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write("# OpenAlex Entities Inspection Report\n\n")
        f.write(f"**Generated on:** {Path().resolve()}\n")
        f.write(f"**Parquet source:** `{parquet_destination_path}`\n\n")

        print("🚀 Starting OpenAlex Entity Inspector")
        print(f"📁 Parquet source: {parquet_destination_path}")
        print(f"📝 Output file: {output_path.absolute()}")

        # Get all available entities
        entities = get_available_entities()

        if not entities:
            error_msg = "❌ No entities with parquet files found"
            print(error_msg)
            f.write(f"{error_msg}\n")
            return

        summary_msg = f"📋 Found {len(entities)} entities: {', '.join(entities)}"
        print(summary_msg)
        f.write(f"**Entities found:** {len(entities)}\n")
        f.write(f"**Entity list:** {', '.join(entities)}\n\n")
        f.write("---\n\n")

        # Process each entity
        for i, entity_name in enumerate(entities, 1):
            process_msg = f"🔄 Processing entity {i}/{len(entities)}: {entity_name}"
            print(process_msg)

            f.write(f"## {i}. {entity_name.upper()}\n\n")

            # Scan the entity
            lazy_df = scan_entity(entity_name)

            if lazy_df is not None:
                # Inspect the dataframe and capture output
                inspection_content = inspect_df_to_markdown(
                    lazy_df, entity_name, n_rows=100_000
                )
                f.write(inspection_content)
            else:
                skip_msg = f"⚠️  Skipping inspection for {entity_name} (scan failed)"
                print(skip_msg)
                f.write("**Status:** ⚠️ Scan failed\n\n")

            # Add separator between entities
            if i < len(entities):
                f.write("---\n\n")

        completion_msg = "🎉 Entity inspection completed!"
        print(completion_msg)
        f.write(f"\n{completion_msg}\n")

    print(f"📄 Report saved to: {output_path.absolute()}")


def inspect_df_to_markdown(
    df: pl.LazyFrame, entity_name: str = "DataFrame", n_rows: int = 5
) -> str:
    """
    Inspects a Polars DataFrame/LazyFrame and returns the inspection as markdown content.

    Args:
        df: Polars LazyFrame or DataFrame to inspect
        entity_name: Name of the entity for display purposes
        n_rows: Number of rows to show in head (default: 5)

    Returns:
        String containing markdown-formatted inspection results
    """
    if df is None:
        return f"**Error:** Cannot inspect {entity_name}: DataFrame is None\n\n"

    content = []

    try:
        # Convert to DataFrame for inspection (collect a small sample)
        sample_df = df.limit(n_rows).collect()

        # Get basic statistics
        total_rows = df.select(pl.len()).collect().item()
        n_columns = len(sample_df.columns)

        content.append(f"**Dimensions:** {total_rows:,} rows × {n_columns} columns")
        content.append(
            f"**Memory usage:** ~{sample_df.estimated_size('mb'):.2f} MB (sample)"
        )
        content.append("")

        # Schema information
        content.append("### Schema")
        content.append("")
        content.append("| # | Column Name | Data Type |")
        content.append("|---|-------------|-----------|")

        schema = sample_df.schema
        for i, (col_name, dtype) in enumerate(schema.items(), 1):
            content.append(f"| {i} | `{col_name}` | `{dtype}` |")

        content.append("")

        # Head preview
        content.append(f"### Sample Data ({n_rows} rows)")
        content.append("")
        content.append("```")
        content.append(str(sample_df))
        content.append("```")
        content.append("")

    except Exception as e:
        content.append(f"**Error inspecting {entity_name}:** {e}")
        content.append("")
        # Try to get basic info without collecting
        try:
            schema = df.schema
            content.append(f"**Schema (lazy):** {len(schema)} columns")
            content.append("")
            content.append("| Column Name | Data Type |")
            content.append("|-------------|-----------|")
            for col_name, dtype in list(schema.items())[:10]:  # Show first 10 columns
                content.append(f"| `{col_name}` | `{dtype}` |")
            if len(schema) > 10:
                content.append(f"| ... | *{len(schema) - 10} more columns* |")
            content.append("")
        except Exception as e2:
            content.append(f"❌ Could not retrieve schema: {e2}")
            content.append("")

    return "\n".join(content)


def process_authors_with_filters(parquet_destination_path: Path) -> None:
    """
    Scans authors folders, applies filters, and exports to test/authors.parquet

    Args:
        parquet_destination_path: Base path containing the authors entity folders
    """
    print("🔄 Processing authors with filters...")

    # Scan all authors parquet files
    lazy_df = scan_entity("authors")

    if lazy_df is None:
        print("❌ Failed to scan authors entity")
        return

    print("✅ Successfully scanned authors data")

    # Apply filters (stub for now - add your filter logic here)
    # filtered_df = apply_author_filters(lazy_df)
    filtered_df = lazy_df

    # Create output directory
    test_output_dir = parquet_destination_path / "test"
    test_output_dir.mkdir(exist_ok=True)

    output_path = test_output_dir / "authors.parquet"

    print(f"💾 Sinking filtered authors data to: {output_path}")

    try:
        # Sink to parquet
        filtered_df.sink_parquet(
            str(output_path), row_group_size=5_000, compression="lz4"
        )
        print("✅ Successfully exported filtered authors data")

        # Show basic stats
        result_df = pl.scan_parquet(str(output_path))
        total_rows = result_df.select(pl.len()).collect().item()
        print(f"📊 Exported {total_rows:,} author records")

    except Exception as e:
        print(f"❌ Error exporting authors data: {e}")


def apply_author_filters(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Applies filters to the authors LazyFrame
    Filters authors who have topics with field IDs 22 and 17, and h-index >= 75th percentile

    Args:
        df: LazyFrame containing authors data

    Returns:
        Filtered LazyFrame
    """
    print(
        "🔧 Applying author filters for topics.field = 22 and 17 + h-index threshold..."
    )

    # First, calculate the 75th percentile of h-index
    print("📊 Calculating 75th percentile of h-index...")
    h_index_75th = (
        df.select(pl.col("summary_stats").struct.field("h_index").quantile(0.75))
        .collect()
        .item()
    )

    print(f"📈 75th percentile h-index: {h_index_75th}")

    # Alternative with explicit column creation for maximum performance
    filtered_df = (
        df.with_columns(
            [
                pl.col("summary_stats").struct.field("h_index").alias("h_index"),
                pl.col("topics")
                .list.eval(
                    pl.element().struct.field("field").struct.field("id") == "22"
                )
                .list.any()
                .alias("has_field_22"),
                pl.col("topics")
                .list.eval(
                    pl.element().struct.field("field").struct.field("id") == "17"
                )
                .list.any()
                .alias("has_field_17"),
            ]
        )
        .filter(
            (pl.col("has_field_22") | pl.col("has_field_17"))
            & (pl.col("h_index") >= h_index_75th)
        )
        .drop(["h_index", "has_field_22", "has_field_17"])
    )

    print(f"✅ Applied filters: topic fields (22, 17) AND h-index >= {h_index_75th}")
    return filtered_df


if __name__ == "__main__":
    # Uncomment the function you want to run:

    # Run full inspection of all entities
    # inspect_all_entities()

    # Process authors with filters
    process_authors_with_filters(parquet_destination_path)

    # Or run specific schema inspections
    # inspect_subfields_schema()
