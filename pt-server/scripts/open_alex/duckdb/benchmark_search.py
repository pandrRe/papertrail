#!/usr/bin/env python3
"""
Benchmark Search: Author Ranking via Hybrid Topic Search

This script benchmarks author ranking based on hybrid search results from topics.
It finds authors who have worked on topics returned by hybrid search and ranks them
by their weighted relevance scores.

The algorithm:
1. Performs hybrid search on topics (FTS + semantic search)
2. Finds authors who have worked on these topics (via author_topics table)
3. Calculates weighted author scores: sum(topic_similarity * author_topic_value)
4. Benchmarks different alpha values for convex combination
5. Times the performance of each approach

Usage:
    python benchmark_search.py [--db-path path/to/database.duckdb] [--query "search term"]
"""

import argparse
import sys
import time
from pathlib import Path
import duckdb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import statistics


def get_script_dir() -> Path:
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()


def initialize_extensions(conn: duckdb.DuckDBPyConnection) -> None:
    """Initialize FTS and VSS extensions"""
    print("Loading extensions...")

    try:
        conn.execute("LOAD fts")
        conn.execute("LOAD vss")
        print("  Extensions loaded")
    except Exception as e:
        print(f"  Error loading extensions: {e}")
        raise


def setup_embedding_function(conn: duckdb.DuckDBPyConnection) -> SentenceTransformer:
    """Setup embedding function and return model"""
    print("Loading SentenceTransformer model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_text_embedding_list(text_list: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = model.encode(text_list, normalize_embeddings=True)
        return embeddings.tolist()

    conn.create_function(
        "get_text_embedding_list",
        get_text_embedding_list,
        return_type="FLOAT[384][]",
    )

    print("  Model loaded and function registered")
    return model


def hybrid_search_topics(
    conn: duckdb.DuckDBPyConnection, query: str, alpha: float = 0.3, limit: int = 10
) -> List[Tuple]:
    """
    Perform hybrid search on topics using configurable alpha for convex combination

    Args:
        conn: Database connection
        query: Search query
        alpha: Weight for BM25 scores (1-alpha for cosine similarity)
        limit: Number of top topics to return

    Returns:
        List of tuples: (topic_id, display_name, hybrid_score, bm25_score, cosine_score)
    """

    hybrid_query = f"""
        WITH fts AS (
            SELECT 
                id,
                display_name,
                fts_main_topics.match_bm25(id, '{query}') as bm25_score
            FROM topics 
        ),
        semantic AS (
            SELECT 
                id,
                display_name,
                array_cosine_similarity(
                    embedding,
                    get_text_embedding_list(['{query}'])[1]
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
            ({alpha} * norm_bm25_score + {1 - alpha} * norm_cosine_score) AS hybrid_score
        FROM normalized_scores
        WHERE (raw_bm25_score > 0 OR raw_cosine_score > 0)
        ORDER BY hybrid_score DESC
        LIMIT {limit}
    """

    return conn.execute(hybrid_query).fetchall()


def rank_authors_by_topics(
    conn: duckdb.DuckDBPyConnection, topic_results: List[Tuple], limit: int = 10
) -> List[Tuple]:
    """
    Rank authors based on their work on the retrieved topics

    Args:
        conn: Database connection
        topic_results: Results from hybrid_search_topics
        limit: Number of top authors to return

    Returns:
        List of tuples: (author_id, display_name, weighted_score, topic_count, topics_details)
    """

    if not topic_results:
        return []

    # Extract topic IDs and their scores
    topic_scores = {
        result[0]: result[6] for result in topic_results
    }  # id -> hybrid_score
    topic_ids = list(topic_scores.keys())

    if not topic_ids:
        return []

    # Create a temporary table for topic scores to avoid SQL injection issues
    temp_table_name = f"temp_topic_scores_{int(time.time() * 1000000) % 1000000}"

    try:
        # Create temporary table
        conn.execute(f"""
            CREATE TEMPORARY TABLE {temp_table_name} (
                topic_id VARCHAR,
                topic_score DOUBLE
            )
        """)

        # Insert topic scores
        for topic_id, score in topic_scores.items():
            conn.execute(
                f"""
                INSERT INTO {temp_table_name} VALUES (?, ?)
            """,
                [topic_id, score],
            )

        # Build the author ranking query using the temporary table
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

        result = conn.execute(author_query).fetchall()

        # Drop temporary table
        conn.execute(f"DROP TABLE {temp_table_name}")

        return result

    except Exception as e:
        # Clean up temporary table if it exists
        try:
            conn.execute(f"DROP TABLE IF EXISTS {temp_table_name}")
        except Exception:
            pass
        raise e


def get_default_test_queries() -> List[str]:
    """Get a diverse set of test queries covering different research domains"""
    return [
        "machine learning",
        "covid vaccine",
        "malaria",
        "immunodeficiency",
        "climate change",
        "quantum computing",
        "gene therapy",
        "neural networks",
        "cancer treatment",
        "renewable energy",
        "diabetes",
        "artificial intelligence",
        "heart disease",
        "solar panels",
        "alzheimer disease",
    ]


def benchmark_alpha_variations(
    conn: duckdb.DuckDBPyConnection,
    queries: List[str],
    alpha_values: List[float] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    iterations: int = 3,
) -> Dict[float, Dict]:
    """
    Benchmark different alpha values for the convex combination across multiple queries

    Args:
        conn: Database connection
        queries: List of search queries to test
        alpha_values: List of alpha values to test
        iterations: Number of iterations per alpha-query combination for averaging

    Returns:
        Dictionary with results for each alpha value
    """

    print(
        f"Benchmarking {len(alpha_values)} alpha values across {len(queries)} queries with {iterations} iterations each..."
    )
    print(f"Total combinations: {len(alpha_values) * len(queries) * iterations}")

    results = {}

    for alpha in alpha_values:
        print(f"\n  Testing alpha = {alpha}")

        alpha_times = []
        alpha_topic_counts = []
        alpha_author_counts = []
        alpha_top_scores = []
        query_results = {}

        for query_idx, query in enumerate(queries, 1):
            print(f"    Query {query_idx}/{len(queries)}: '{query}'")

            query_times = []
            query_results_list = []

            for iteration in range(iterations):
                start_time = time.time()

                # Hybrid search
                topic_results = hybrid_search_topics(conn, query, alpha=alpha, limit=10)

                # Author ranking
                author_results = rank_authors_by_topics(conn, topic_results, limit=10)

                end_time = time.time()
                duration = end_time - start_time

                query_times.append(duration)
                query_results_list.append((topic_results, author_results))

                # Collect metrics for aggregation
                alpha_times.append(duration)
                alpha_topic_counts.append(len(topic_results))
                alpha_author_counts.append(len(author_results))
                alpha_top_scores.append(author_results[0][2] if author_results else 0)

            # Store best result for this query (first iteration)
            best_topics, best_authors = query_results_list[0]
            query_results[query] = {
                "topic_results": best_topics,
                "author_results": best_authors,
                "avg_time": statistics.mean(query_times),
                "topic_count": len(best_topics),
                "author_count": len(best_authors),
                "top_score": best_authors[0][2] if best_authors else 0,
            }

            print(
                f"      {statistics.mean(query_times):.3f}s, {len(best_topics)} topics, {len(best_authors)} authors"
            )

        # Calculate aggregate statistics across all queries
        avg_time = statistics.mean(alpha_times)
        std_time = statistics.stdev(alpha_times) if len(alpha_times) > 1 else 0
        min_time = min(alpha_times)
        max_time = max(alpha_times)
        avg_topics = statistics.mean(alpha_topic_counts)
        avg_authors = statistics.mean(alpha_author_counts)
        avg_top_score = statistics.mean(alpha_top_scores)

        results[alpha] = {
            "avg_time": avg_time,
            "std_time": std_time,
            "min_time": min_time,
            "max_time": max_time,
            "avg_topics": avg_topics,
            "avg_authors": avg_authors,
            "avg_top_score": avg_top_score,
            "query_results": query_results,
            "iterations": iterations,
            "total_queries": len(queries),
        }

        print(
            f"    Alpha {alpha} summary: {avg_time:.3f}s (+/-{std_time:.3f}s), "
            f"{avg_topics:.1f} topics, {avg_authors:.1f} authors, top_score: {avg_top_score:.3f}"
        )

    return results


def print_detailed_results(
    alpha: float, alpha_data: Dict, specific_query: str = None
) -> None:
    """Print detailed results for a specific alpha value"""

    print(f"\nDetailed Results for alpha = {alpha}")
    print("=" * 80)

    if specific_query and specific_query in alpha_data["query_results"]:
        # Show results for specific query
        query_data = alpha_data["query_results"][specific_query]
        print(f"Query: '{specific_query}'")

        topic_results = query_data["topic_results"]
        author_results = query_data["author_results"]

        print("\nTop Topics (Hybrid Search):")
        for i, result in enumerate(topic_results[:5], 1):
            _, display_name, _, _, norm_bm25, norm_cosine, hybrid_score = result
            print(f"  {i}. {display_name}")
            print(
                f"     Hybrid: {hybrid_score:.3f} (BM25: {norm_bm25:.3f}, Cosine: {norm_cosine:.3f})"
            )

        print("\nTop Authors (Ranked by Topic Relevance):")
        for i, result in enumerate(author_results[:5], 1):
            _, display_name, total_score, topic_count, topics_details = result
            print(f"  {i}. {display_name}")
            print(f"     Score: {total_score:.3f}, Topics: {topic_count}")

            # Show top contributing topics
            if topics_details:
                sorted_topics = sorted(
                    topics_details, key=lambda x: x["contribution"], reverse=True
                )
                for j, topic in enumerate(sorted_topics[:3], 1):
                    print(
                        f"       {j}. {topic['topic_name']}: {topic['contribution']:.3f}"
                    )
                    print(
                        f"          (author_value: {topic['author_value']:.3f}, topic_score: {topic['topic_score']:.3f})"
                    )
    else:
        # Show aggregate results across all queries
        print(f"Aggregate Results Across {alpha_data['total_queries']} Queries")
        print(
            f"Average time: {alpha_data['avg_time']:.3f}s (+/-{alpha_data['std_time']:.3f}s)"
        )
        print(f"Average topics found: {alpha_data['avg_topics']:.1f}")
        print(f"Average authors found: {alpha_data['avg_authors']:.1f}")
        print(f"Average top author score: {alpha_data['avg_top_score']:.3f}")

        print("\nPer-Query Breakdown:")
        for query, query_data in alpha_data["query_results"].items():
            print(
                f"  '{query}': {query_data['avg_time']:.3f}s, "
                f"{query_data['topic_count']} topics, {query_data['author_count']} authors, "
                f"top_score: {query_data['top_score']:.3f}"
            )


def print_benchmark_summary(results: Dict[float, Dict]) -> None:
    """Print summary of all benchmark results across multiple queries"""

    total_queries = next(iter(results.values()))["total_queries"]

    print(f"\nBenchmark Summary - Across {total_queries} Queries")
    print("=" * 100)
    print(
        f"{'Alpha':<8} {'Avg Time (s)':<12} {'Std Dev':<10} {'Avg Topics':<12} {'Avg Authors':<12} {'Avg Top Score':<15}"
    )
    print("-" * 100)

    for alpha in sorted(results.keys()):
        data = results[alpha]

        print(
            f"{alpha:<8.1f} {data['avg_time']:<12.3f} {data['std_time']:<10.3f} "
            f"{data['avg_topics']:<12.1f} {data['avg_authors']:<12.1f} {data['avg_top_score']:<15.3f}"
        )

    # Find best performing alpha by different metrics
    best_by_time = min(results.keys(), key=lambda a: results[a]["avg_time"])
    best_by_top_score = max(results.keys(), key=lambda a: results[a]["avg_top_score"])
    best_by_authors = max(results.keys(), key=lambda a: results[a]["avg_authors"])

    print("\nBest Results:")
    print(
        f"  Fastest: alpha = {best_by_time} ({results[best_by_time]['avg_time']:.3f}s)"
    )
    print(
        f"  Highest avg top score: alpha = {best_by_top_score} ({results[best_by_top_score]['avg_top_score']:.3f})"
    )
    print(
        f"  Most authors found: alpha = {best_by_authors} ({results[best_by_authors]['avg_authors']:.1f} authors)"
    )

    # Show query-specific best performers
    print(f"\nPer-Query Best Alpha Values (by top author score):")
    query_best = {}
    for alpha, alpha_data in results.items():
        for query, query_data in alpha_data["query_results"].items():
            if (
                query not in query_best
                or query_data["top_score"] > query_best[query]["score"]
            ):
                query_best[query] = {"alpha": alpha, "score": query_data["top_score"]}

    for query, best_data in query_best.items():
        print(
            f"  '{query}': alpha = {best_data['alpha']} (score: {best_data['score']:.3f})"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark author ranking via hybrid topic search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic benchmark with 15 default diverse queries
    python benchmark_search.py
    
    # Test single query
    python benchmark_search.py --query "machine learning neural networks"
    
    # Test custom queries from file
    python benchmark_search.py --queries-file my_queries.txt
    
    # Quick test with fewer iterations
    python benchmark_search.py --iterations 1 --detailed-alpha 0.3
    
    # Show detailed results for specific query and alpha
    python benchmark_search.py --detailed-alpha 0.3 --detailed-query "covid vaccine"
    
    # Custom alpha range and database
    python benchmark_search.py --alpha-range 0.2 0.8 0.1 --db-path /path/to/openalex.duckdb
        """,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="openalex.duckdb",
        help="Path to the DuckDB database file (default: openalex.duckdb)",
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Single search query to test (if not provided, uses default set of 15 diverse queries)",
    )

    parser.add_argument(
        "--queries-file",
        type=str,
        help="Path to file containing queries (one per line)",
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations per alpha-query combination for averaging (default: 3)",
    )

    parser.add_argument(
        "--detailed-alpha",
        type=float,
        help="Show detailed results for specific alpha value (e.g., 0.3)",
    )

    parser.add_argument(
        "--detailed-query",
        type=str,
        help="Show detailed results for specific query (requires --detailed-alpha)",
    )

    parser.add_argument(
        "--alpha-range",
        nargs=3,
        type=float,
        metavar=("START", "STOP", "STEP"),
        help="Custom alpha range: start stop step (e.g., --alpha-range 0.1 1.0 0.1)",
    )

    args = parser.parse_args()

    # Resolve database path
    db_path = Path(args.db_path).resolve()

    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        sys.exit(1)

    # Determine queries to use
    if args.query:
        # Single query mode
        queries = [args.query]
        print(f"Using single query: '{args.query}'")
    elif args.queries_file:
        # Read queries from file
        try:
            with open(args.queries_file, "r") as f:
                queries = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(queries)} queries from {args.queries_file}")
        except Exception as e:
            print(f"Error reading queries file: {e}")
            sys.exit(1)
    else:
        # Use default diverse query set
        queries = get_default_test_queries()
        print(f"Using default set of {len(queries)} diverse queries")

    # Generate alpha values
    if args.alpha_range:
        start, stop, step = args.alpha_range
        alpha_values = [
            round(start + i * step, 1) for i in range(int((stop - start) / step))
        ]
    else:
        alpha_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    print("\nAuthor Ranking Benchmark via Hybrid Topic Search")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Queries: {len(queries)} total")
    if len(queries) <= 5:
        print(f"  {queries}")
    else:
        print(f"  {queries[:3]} ... {queries[-2:]}")
    print(f"Alpha values: {alpha_values}")
    print(f"Iterations: {args.iterations}")

    # Connect to database
    try:
        conn = duckdb.connect(str(db_path))
        print("Connected to database")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Initialize extensions and setup
        initialize_extensions(conn)
        setup_embedding_function(conn)

        # Run benchmarks
        start_total = time.time()
        results = benchmark_alpha_variations(
            conn, queries, alpha_values, args.iterations
        )
        end_total = time.time()

        print(f"\nBenchmark completed in {end_total - start_total:.2f}s")

        # Print summary
        print_benchmark_summary(results)

        # Print detailed results if requested
        if args.detailed_alpha and args.detailed_alpha in results:
            data = results[args.detailed_alpha]
            print_detailed_results(
                args.detailed_alpha, data, specific_query=args.detailed_query
            )

    finally:
        conn.close()
        print("\nDatabase connection closed")


if __name__ == "__main__":
    main()
