from duckdb import DuckDBPyConnection
from .logger import logger


def setup_prepared_statements(duckdb_conn: DuckDBPyConnection) -> None:
    """Setup macros for DuckDB queries."""

    logger.info("Setting up DuckDB macros...")

    # Hybrid search table macro
    hybrid_search_macro = """
        CREATE OR REPLACE TEMP MACRO hybrid_search(query_text, alpha, limit_count) AS TABLE
        WITH fts AS (
            SELECT 
                id,
                display_name,
                fts_main_topics.match_bm25(id, query_text) as bm25_score
            FROM topics
        ),
        semantic AS (
            SELECT 
                id,
                display_name,
                array_cosine_similarity(
                    embedding,
                    get_text_embedding_list([query_text])[1]
                ) as cosine_score
            FROM topics 
            WHERE embedding IS NOT NULL
        ),
        normalized_scores AS (
            SELECT 
                COALESCE(fts.id, semantic.id) as id,
                COALESCE(fts.display_name, semantic.display_name) as display_name,
                COALESCE(fts.bm25_score, 0) as raw_bm25_score,
                COALESCE(semantic.cosine_score, 0) as raw_cosine_score,
                -- Min-max normalization for BM25 scores
                CASE 
                    WHEN (SELECT MAX(bm25_score) FROM fts WHERE bm25_score > 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0) = 0 
                    THEN 0
                    ELSE (COALESCE(fts.bm25_score, 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0)) / 
                         NULLIF((SELECT MAX(bm25_score) FROM fts WHERE bm25_score > 0) - (SELECT MIN(bm25_score) FROM fts WHERE bm25_score > 0), 0)
                END as norm_bm25_score,
                -- Cosine similarity is already normalized [0,1], but ensure it's positive
                GREATEST(COALESCE(semantic.cosine_score, 0), 0) as norm_cosine_score
            FROM fts
            FULL OUTER JOIN semantic ON fts.id = semantic.id
        )
        SELECT 
            id,
            display_name,
            raw_bm25_score,
            raw_cosine_score,
            norm_bm25_score,
            norm_cosine_score,
            -- Convex combination with configurable alpha
            (alpha * norm_bm25_score + (1 - alpha) * norm_cosine_score) AS hybrid_score
        FROM normalized_scores
        WHERE (raw_bm25_score > 0 OR raw_cosine_score > 0)
        ORDER BY hybrid_score DESC
        LIMIT limit_count
    """

    duckdb_conn.execute(hybrid_search_macro)

    logger.info("DuckDB macros and prepared statements setup completed")


def save_hybrid_search_to_temp_table(
    duckdb_conn: DuckDBPyConnection,
    table_name: str,
    query: str,
    alpha: float = 0.2,
    limit: int = 10,
) -> None:
    """Save the hybrid search results to a temporary table using macro."""

    create_table_query = f"""
        CREATE TEMP TABLE {table_name} AS 
        SELECT 
            id as topic_id, 
            display_name, 
            raw_bm25_score, 
            raw_cosine_score, 
            norm_bm25_score, 
            norm_cosine_score, 
            hybrid_score as topic_score 
        FROM hybrid_search($1, $2, $3)
    """

    duckdb_conn.execute(create_table_query, [query, alpha, limit])


def rank_authors(
    duckdb_conn: DuckDBPyConnection, temp_table_name: str, limit: int = 10
) -> list:
    """Rank authors based on their relevance to topics and cleanup temp table."""

    author_query = f"""
        WITH relevant_topics AS (
            SELECT topic_id, topic_score FROM {temp_table_name}
        ),
        author_topic_scores AS (
            SELECT
                author_topics.author_id,
                a.display_name,
                author_topics.topic_id,
                t.display_name as topic_name,
                author_topics.value as author_topic_value,
                rt.topic_score,
                (rt.topic_score * author_topics.value) as weighted_contribution
            FROM author_topics
            JOIN authors a ON (author_topics.author_id = a.id)
            JOIN topics t ON (author_topics.topic_id = t.id)
            JOIN relevant_topics rt ON (author_topics.topic_id = rt.topic_id)
        ),
        aggregated_scores AS (
            SELECT 
                author_id,
                display_name,
                SUM(weighted_contribution) as total_weighted_score,
                COUNT(DISTINCT topic_id) as topic_count,
                ARRAY_AGG(
                    {{'topic_id': topic_id, 
                     'topic_name': topic_name, 
                     'author_value': author_topic_value, 
                     'topic_score': topic_score, 
                     'contribution': weighted_contribution}}
                ) as topics_details
            FROM author_topic_scores
            GROUP BY author_id, display_name
        )
        SELECT 
            author_id,
            display_name,
            total_weighted_score,
            topic_count,
            topics_details
        FROM aggregated_scores
        ORDER BY total_weighted_score DESC
        LIMIT {limit}
    """

    try:
        results = duckdb_conn.execute(author_query).fetchall()

        # Drop temporary table
        duckdb_conn.execute(f"DROP TABLE {temp_table_name}")

        return results
    except Exception as e:
        # Ensure temp table is dropped even if query fails
        try:
            duckdb_conn.execute(f"DROP TABLE {temp_table_name}")
        except Exception:
            pass
        raise e
