import httpx
import duckdb
import time
from typing import Dict, Any, List, Tuple
from ..internal.entities import AuthorWorksResult
from ..internal.logger import logger

OPEN_ALEX_API_URL = "https://api.openalex.org/"

default_works_fields = [
    # Basic fields matching new schema
    "id",
    "doi",
    "title",
    "display_name",
    "publication_date",
    "language",
    "type",
    "open_access",  # For extracting oa_url
    "ids",
    "authorships",
    "created_date",
    "updated_date",
    "relevance_score",
]


async def get_works_page(query: str, page: int):
    start_time = time.perf_counter()

    selected_str = ",".join(default_works_fields)
    queries = {
        "search": query,
        "page": page,
        "per-page": 200,
        "select": selected_str,
        "filter": "is_paratext:false",
    }
    url = f"{OPEN_ALEX_API_URL}works?{httpx.QueryParams(queries)}"

    request_start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        request_duration = time.perf_counter() - request_start

        json_start = time.perf_counter()
        result = response.json()
        json_duration = time.perf_counter() - json_start

        total_duration = time.perf_counter() - start_time

        logger.info(
            f"OpenAlex API page {page}: request={request_duration:.3f}s, json_parse={json_duration:.3f}s, total={total_duration:.3f}s"
        )
        return result


def insert_or_get_api_query(
    duckdb_conn: duckdb.DuckDBPyConnection, query_text: str, max_pages: int
) -> str:
    """Insert or replace API query record and return the query_text."""
    # Insert or replace query
    cursor = duckdb_conn.execute(
        """INSERT INTO api_queries (query_text, max_pages, created_at) 
           VALUES (?, ?, current_localtimestamp()) 
           ON CONFLICT (query_text) DO UPDATE SET 
           max_pages = EXCLUDED.max_pages,
           created_at = current_localtimestamp()
           RETURNING query_text""",
        [query_text, max_pages],
    )
    result = cursor.fetchall()
    return result[0][0]


def get_work_insert_params(
    works_data: List[Dict[str, Any]], query_text: str, page: int
) -> Tuple[List[List], List[List]]:
    """Prepare batch insert parameters for works and work-query relationships."""
    work_params = []
    relationship_params = []

    for position, work in enumerate(works_data):
        work_id = work.get("id")
        relevance_score = work.get("relevance_score", 0.0)

        if work_id:
            # Extract oa_url from open_access object
            open_access = work.get("open_access", {})
            oa_url = open_access.get("oa_url") if open_access else None

            # Transform authorships to simplified format
            authorships = work.get("authorships", [])
            simplified_authorships = []
            for authorship in authorships:
                author = authorship.get("author", {})
                simplified_authorships.append(
                    {
                        "id": author.get("id"),
                        "display_name": author.get("display_name"),
                        "orcid": author.get("orcid"),
                    }
                )

            # Prepare work data for batch insert (order must match new schema)
            work_params.append(
                [
                    work.get("id"),  # $1
                    work.get("doi"),  # $2
                    work.get("title"),  # $3
                    work.get("display_name"),  # $4
                    work.get("publication_date"),  # $5
                    work.get("language"),  # $6
                    work.get("type"),  # $7
                    oa_url,  # $8
                    work.get("ids"),  # $9
                    simplified_authorships,  # $10
                    work.get("created_date"),  # $11
                    work.get("updated_date"),  # $12
                ]
            )

            # Prepare relationship data for batch insert
            relationship_params.append(
                [
                    query_text,
                    work_id,
                    page,
                    position,
                    relevance_score,
                ]
            )

    return work_params, relationship_params


async def get_works(
    query: str, max_pages: int = 5, duckdb_conn: duckdb.DuckDBPyConnection = None
) -> str:
    """
    Fetch works from OpenAlex API and store in DuckDB tables.

    Returns:
        str: Query text.
    """
    start_time = time.perf_counter()

    if duckdb_conn is None:
        raise ValueError("DuckDB connection is required")

    # Insert or get query record
    query_text = insert_or_get_api_query(duckdb_conn, query, max_pages)

    all_works = []
    total_results = 0

    for page in range(1, max_pages + 1):
        result = await get_works_page(query, page)

        if "results" in result:
            works_data = result["results"]
            total_results = result.get("meta", {}).get("count", 0)

            # Prepare batch data for works and relationships
            prep_start = time.perf_counter()
            work_params, relationship_params = get_work_insert_params(
                works_data, query_text, page
            )
            prep_duration = time.perf_counter() - prep_start
            logger.info(
                f"Data preparation page {page}: {len(works_data)} works, duration={prep_duration:.3f}s"
            )

            # Batch insert works
            if work_params:
                # Insert works
                works_insert_start = time.perf_counter()
                duckdb_conn.executemany(
                    """
                    INSERT OR REPLACE INTO works (
                        id, doi, title, display_name, publication_date,
                        language, type, oa_url, ids, authorships,
                        created_date, updated_date
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                    )
                    """,
                    work_params,
                )
                works_insert_duration = time.perf_counter() - works_insert_start

                # Insert relationships
                relations_insert_start = time.perf_counter()
                duckdb_conn.executemany(
                    """INSERT OR REPLACE INTO works_api_queries 
                       (query_text, work_id, page_number, position_in_page, relevance_score, created_at) 
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    relationship_params,
                )
                relations_insert_duration = time.perf_counter() - relations_insert_start

                logger.info(
                    f"Database inserts page {page}: works={works_insert_duration:.3f}s, relations={relations_insert_duration:.3f}s"
                )

            all_works.extend(works_data)

            # If we got fewer results than expected, break early
            if len(works_data) < 200:
                break
        else:
            raise ValueError(
                f"Unexpected API response structure: missing 'results' key in response from page {page}"
            )

    # Update total results in api_queries table
    update_start = time.perf_counter()
    duckdb_conn.execute(
        "UPDATE api_queries SET total_results = ? WHERE query_text = ?",
        [total_results, query_text],
    )
    update_duration = time.perf_counter() - update_start

    total_duration = time.perf_counter() - start_time
    logger.info(
        f"get_works completed: total_duration={total_duration:.3f}s, pages={max_pages}, total_results={total_results}, update={update_duration:.3f}s"
    )

    return query_text


def group_works_by_author(
    query: str, duckdb_conn: duckdb.DuckDBPyConnection
) -> List[AuthorWorksResult]:
    """
    Group works by their authors for a given query text.
    """
    start_time = time.perf_counter()

    query = """
    WITH
        ranked_works AS (
            w.*,
            fts_main_works.match_bm25(
                w.display_name,
                ?
            ) as fts_score
            FROM works w
            WHERE fts_score > 0
            ORDER BY fts_score DESC
            LIMIT 1000
        ),
        ranked_works_authorships AS (
            SELECT
                w.*,
                a.*
            FROM works w
            JOIN authorships aw ON aw.work_id = w.id
            JOIN authors a ON aw.author_id = a.id
        ),
        query_works AS (
            SELECT 
                w.id,
                STRUCT_PACK(
                    display_name := w.display_name,
                    publication_date := w.publication_date,
                    doi := w.doi,
                    type := w.type,
                    authorships := w.authorships,
                    url := w.oa_url
                ) AS work_summary,
                unnest(w.authorships) AS authorship,
                wq.relevance_score
            FROM works w
            JOIN works_api_queries wq ON w.id = wq.work_id AND wq.query_text = ?
        ),
        author_works AS (
            SELECT
                authorship.id AS id,
                COUNT(DISTINCT id) AS work_count,
                ARRAY_AGG(DISTINCT work_summary) AS works,
                AVG(relevance_score) * LOG(COUNT(DISTINCT id) + 1) AS author_score
            FROM query_works
            GROUP BY authorship.id
            ORDER BY author_score DESC, work_count DESC
            LIMIT 10
        ),
        author_affiliations_agg AS (
            SELECT 
                aa.author_id,
                ARRAY_AGG(STRUCT_PACK(
                    institution_id := aa.institution_id,
                    institution_name := i.display_name,
                    years := aa.years
                )) AS affiliations
            FROM author_affiliations aa
            JOIN institutions i ON aa.institution_id = i.id
            WHERE EXISTS (SELECT 1 FROM author_works aw WHERE aw.id = aa.author_id)
            GROUP BY aa.author_id
        )
    SELECT 
        aw.id,
        aw.work_count,
        aw.works,
        aw.author_score,
        COALESCE(aaa.affiliations, []) AS affiliations
    FROM author_works aw
    LEFT JOIN author_affiliations_agg aaa ON aw.id = aaa.author_id
    """

    # Execute query
    query_start = time.perf_counter()
    result = duckdb_conn.execute(query, [query_text])
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    query_duration = time.perf_counter() - query_start

    # Convert to objects
    conversion_start = time.perf_counter()
    raw_results = [dict(zip(columns, row)) for row in rows]
    author_results = [AuthorWorksResult(**result) for result in raw_results]
    conversion_duration = time.perf_counter() - conversion_start

    total_duration = time.perf_counter() - start_time

    logger.info(
        f"Group authors query: sql={query_duration:.3f}s, conversion={conversion_duration:.3f}s, total={total_duration:.3f}s, authors={len(author_results)}"
    )

    return author_results


async def search_author(
    query: str, duckdb_conn: duckdb.DuckDBPyConnection
) -> List[AuthorWorksResult]:
    start_time = time.perf_counter()

    # Group by authors
    group_start = time.perf_counter()
    authors = group_works_by_author(query, duckdb_conn)
    group_duration = time.perf_counter() - group_start

    total_duration = time.perf_counter() - start_time
    logger.info(
        f"search_author completed: total={total_duration:.3f}s, group_authors={group_duration:.3f}s, authors_found={len(authors)}"
    )

    return authors
