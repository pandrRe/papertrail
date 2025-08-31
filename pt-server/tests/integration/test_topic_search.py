import os
import pytest
import duckdb
from app.dependencies import ModelManager
from app.internal.duckdb import setup_prepared_statements
from app.sources.open_alex import rank_topics_by_query, rank_authors_by_topic_relevance


@pytest.fixture(scope="module")
def duckdb_connection():
    """Setup DuckDB connection for integration tests."""
    # Get DuckDB path from environment variable or use test default
    test_db_path = os.getenv("TEST_DUCKDB_PATH", ":memory:")

    conn = duckdb.connect(test_db_path)

    # Install and load extensions
    conn.execute("INSTALL fts")
    conn.execute("LOAD fts")
    conn.execute("INSTALL vss")
    conn.execute("LOAD vss")

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture(scope="module")
def model_manager():
    """Setup ModelManager for tests."""
    manager = ModelManager()
    manager.initialize()
    return manager


@pytest.fixture(scope="module")
def setup_duckdb_with_model(duckdb_connection, model_manager):
    """Setup DuckDB with embedding function and prepared statements.

    Assumes the database already contains the necessary tables:
    - topics (id, display_name, embedding)
    - authors (id, display_name)
    - author_topics (author_id, topic_id, value)
    - fts_main_topics (FTS index)
    """
    # Setup embedding function
    model = model_manager.get_model()

    def get_text_embedding_list(text_list: list[str]):
        """Generate embeddings for a list of texts"""
        embeddings = model.encode(text_list, normalize_embeddings=True)
        return embeddings

    duckdb_connection.create_function(
        "get_text_embedding_list",
        get_text_embedding_list,
        return_type="FLOAT[384][]",
    )

    # Setup prepared statements
    setup_prepared_statements(duckdb_connection)

    return duckdb_connection


class TestTopicSearch:
    """Integration tests for topic search functionality."""

    def test_rank_topics_by_query_returns_table_name(self, setup_duckdb_with_model):
        """Test that rank_topics_by_query returns a valid temp table name."""
        conn = setup_duckdb_with_model

        result = rank_topics_by_query(
            query="machine learning", duckdb_conn=conn, alpha=0.5, limit=5
        )

        # Should return a string (table name)
        assert isinstance(result, str)
        assert result.startswith("temp_hybrid_search_")

        # Verify table exists and has data
        table_check = conn.execute(f"SELECT COUNT(*) FROM {result}").fetchone()[0]
        assert table_check >= 0  # Table should exist (may be empty if no matches)

        # Clean up the temp table
        conn.execute(f"DROP TABLE {result}")

    def test_rank_topics_by_query_with_different_parameters(
        self, setup_duckdb_with_model
    ):
        """Test rank_topics_by_query with different alpha and limit values."""
        conn = setup_duckdb_with_model

        # Test with semantic focus (low alpha)
        result1 = rank_topics_by_query(
            query="deep neural networks",
            duckdb_conn=conn,
            alpha=0.1,  # Focus on semantic similarity
            limit=3,
        )

        # Test with BM25 focus (high alpha)
        result2 = rank_topics_by_query(
            query="deep neural networks",
            duckdb_conn=conn,
            alpha=0.9,  # Focus on BM25
            limit=3,
        )

        # Both should return table names
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert result1 != result2  # Should be different tables

        # Clean up
        conn.execute(f"DROP TABLE {result1}")
        conn.execute(f"DROP TABLE {result2}")

    def test_rank_authors_by_topic_relevance(self, setup_duckdb_with_model):
        """Test author ranking based on topic relevance."""
        conn = setup_duckdb_with_model

        # First get topic search results
        topic_table = rank_topics_by_query(
            query="machine learning", duckdb_conn=conn, alpha=0.5, limit=5
        )

        # Then rank authors
        authors = rank_authors_by_topic_relevance(
            search_results_table=topic_table, duckdb_conn=conn
        )

        # Should return a list of author results
        assert isinstance(authors, list)

        # If we have results, verify structure
        if authors:
            author = authors[0]
            assert len(author) == 5  # Should have 5 columns
            # Columns: author_id, display_name, total_weighted_score, topic_count, topics_details
            assert isinstance(author[0], str)  # author_id
            assert isinstance(author[1], str)  # display_name
            assert isinstance(author[2], (int, float))  # total_weighted_score
            assert isinstance(author[3], int)  # topic_count
            # topics_details is an array/list

    def test_end_to_end_topic_search_workflow(self, setup_duckdb_with_model):
        """Test the complete workflow from topic search to author ranking."""
        conn = setup_duckdb_with_model

        # Step 1: Search for topics
        topic_table = rank_topics_by_query(
            query="artificial intelligence",
            duckdb_conn=conn,
            alpha=0.3,  # Slight semantic focus
            limit=10,
        )

        assert isinstance(topic_table, str)

        # Step 2: Rank authors based on those topics
        authors = rank_authors_by_topic_relevance(
            search_results_table=topic_table, duckdb_conn=conn
        )

        assert isinstance(authors, list)

        # Verify the workflow completed without errors
        # The temp table should be automatically cleaned up by rank_authors_by_topic_relevance

        # Verify temp table was cleaned up
        with pytest.raises(Exception):  # Should raise error because table doesn't exist
            conn.execute(f"SELECT COUNT(*) FROM {topic_table}").fetchone()


class TestDuckDBSetup:
    """Test DuckDB setup and configuration."""

    def test_embedding_function_available(self, setup_duckdb_with_model):
        """Test that the get_text_embedding_list function is available."""
        conn = setup_duckdb_with_model

        # Test the embedding function
        result = conn.execute(
            "SELECT get_text_embedding_list(['hello world'])"
        ).fetchone()[0]

        assert isinstance(result, list)
        assert len(result) == 1  # One embedding for one text
        assert len(result[0]) == 384  # SentenceTransformer dimension
        assert all(isinstance(x, float) for x in result[0])  # All elements are floats
