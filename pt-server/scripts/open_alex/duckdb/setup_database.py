#!/usr/bin/env python3
"""
DuckDB OpenAlex Database Setup Script

This script creates a DuckDB database file and sets up all the OpenAlex entity tables
as defined in duckdb_tables.sql.

Usage:
    python setup_database.py [--db-path path/to/database.duckdb]
"""

import argparse
import sys
from pathlib import Path
import duckdb


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def read_sql_file(sql_path: Path) -> str:
    """Read the SQL file and return its contents"""
    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: SQL file not found at {sql_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        sys.exit(1)


def setup_database(db_path: Path, sql_content: str) -> None:
    """Create the database and execute the SQL schema"""
    print(f"Setting up DuckDB database at: {db_path}")

    # Create directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Connect to DuckDB (creates file if it doesn't exist)
        conn = duckdb.connect(str(db_path))

        print("Connected to database successfully")
        print("Executing schema creation...")

        # Execute the SQL schema
        conn.execute(sql_content)

        print("Schema created successfully!")

        # Get table count to verify
        result = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchone()
        table_count = result[0] if result else 0

        print(f"Created {table_count} tables")

        # List all tables
        tables = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY table_name"
        ).fetchall()
        if tables:
            print("\nTables created:")
            for table in tables:
                print(f"  - {table[0]}")

        # Get index count
        indexes = conn.execute("SELECT COUNT(*) FROM duckdb_indexes()").fetchone()
        index_count = indexes[0] if indexes else 0
        print(f"\nCreated {index_count} indexes")

        conn.close()
        print(f"\nDatabase setup complete! File: {db_path}")

    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Setup DuckDB database with OpenAlex schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create database in default location
    python setup_database.py
    
    # Create database at specific path
    python setup_database.py --db-path /path/to/openalex.duckdb
    
    # Create database in current directory
    python setup_database.py --db-path ./openalex.duckdb
        """,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="openalex.duckdb",
        help="Path to the DuckDB database file (default: openalex.duckdb)",
    )

    parser.add_argument(
        "--sql-file",
        type=str,
        help="Path to SQL schema file (default: duckdb_tables.sql in same directory)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing database file if it exists",
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = get_script_dir()
    db_path = Path(args.db_path).resolve()

    if args.sql_file:
        sql_path = Path(args.sql_file).resolve()
    else:
        sql_path = script_dir / "duckdb_tables.sql"

    # Check if database already exists
    if db_path.exists() and not args.force:
        response = input(f"Database file {db_path} already exists. Overwrite? (y/N): ")
        if response.lower() not in ["y", "yes"]:
            print("Aborted.")
            sys.exit(0)

    # Verify SQL file exists
    if not sql_path.exists():
        print(f"Error: SQL schema file not found at {sql_path}")
        sys.exit(1)

    print("DuckDB OpenAlex Database Setup")
    print("=" * 40)
    print(f"Database file: {db_path}")
    print(f"SQL schema file: {sql_path}")
    print(f"Database size: {db_path.stat().st_size if db_path.exists() else 0} bytes")
    print()

    # Read SQL content
    sql_content = read_sql_file(sql_path)
    print(f"Loaded SQL schema ({len(sql_content)} characters)")

    # Setup database
    setup_database(db_path, sql_content)


if __name__ == "__main__":
    main()
