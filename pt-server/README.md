# Papertrail Server

## Development

### Starting the Server

```bash
uv run fastapi dev
```

## Testing

The test suite is organized into unit and integration tests:

### Unit Tests

Fast tests that don't require external dependencies or database connections:

```bash
uv run pytest tests/unit/ -v
```

### Integration Tests

Tests that require a populated DuckDB database with real data:

```bash
# Set the test database path (optional, defaults to :memory:)
export TEST_DUCKDB_PATH=/path/to/test/database.db

# Run integration tests
uv run pytest tests/integration/ -v
```

**Note**: Integration tests assume the database contains:

- `topics` table with `id`, `display_name`, `embedding` columns
- `authors` table with `id`, `display_name` columns
- `author_topics` table with `author_id`, `topic_id`, `value` columns
- `fts_main_topics` FTS index for topic search

### All Tests

```bash
uv run pytest tests/ -v
```

### Test-Specific Commands

```bash
# Run specific test file
uv run pytest tests/integration/test_topic_search.py -v

# Run specific test function
uv run pytest tests/integration/test_topic_search.py::TestTopicSearch::test_rank_topics_by_query_returns_table_name -v

# Run tests with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

- STOPPED json -> parquet at batch 149. resume at 150.
- uploaded to db up to page 231
- arimo, ibm plex mono
