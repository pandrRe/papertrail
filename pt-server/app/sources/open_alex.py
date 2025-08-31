import time
from duckdb import DuckDBPyConnection
from ..internal.duckdb import save_hybrid_search_to_temp_table, rank_authors


def rank_topics_by_query(
    query: str,
    duckdb_conn: DuckDBPyConnection,
    alpha: float = 0.2,
    limit: int = 50,
) -> str:
    """
    Rank topics based on a given query using hybrid search (BM25 + semantic similarity).

    Args:
        query (str): The search query to rank topics against.
        transformer (SentenceTransformer): The sentence transformer model (unused, kept for compatibility).
        duckdb_conn (DuckDBPyConnection): DuckDB connection.
        alpha (float): Weight for BM25 vs semantic similarity (0=semantic only, 1=BM25 only).
        limit (int): Maximum number of results to return.

    Returns:
        str: Temporary table name where results are stored.
    """
    table_name = f"temp_hybrid_search_{time.time_ns()}"
    save_hybrid_search_to_temp_table(duckdb_conn, table_name, query, alpha, limit)
    return table_name


def rank_authors_by_topic_relevance(
    search_results_table: str, duckdb_conn: DuckDBPyConnection
) -> list:
    """
    Rank authors based on their relevance to the topics in the search results.

    Args:
        search_results_table (str): The temporary table with search results.
        duckdb_conn (DuckDBPyConnection): DuckDB connection.

    Returns:
        list: Authors ranked.
    """
    authors = rank_authors(duckdb_conn, search_results_table, limit=10)
    return authors
