import { arrayValue, DuckDBConnection } from "@duckdb/node-api";
import { generateEmbedding } from "./ai";
import { AuthorRankingResult } from "./types";

const parquetPath = process.env.DENORM_PARQUET_PATH;
if (!parquetPath) {
  throw new Error("DENORM_PARQUET_PATH environment variable is not set");
}

const authorsQuery = `\
WITH 
-- Step 1: Get top K topics using HNSW index for fast similarity search
top_topics AS (
  SELECT
    id AS topic_id,
    display_name AS topic_name,
    (array_cosine_similarity(embedding, $query_embedding::FLOAT[768]) + 1) / 2 AS topic_relevance_score,
    ROW_NUMBER() OVER (ORDER BY array_cosine_similarity(embedding, $query_embedding::FLOAT[768]) DESC) AS topic_rank
  FROM topics
  ORDER BY topic_relevance_score DESC
  LIMIT 5
),
author_topics_result AS (
  SELECT
    author_id,
    ANY_VALUE(display_name) AS display_name,
    ANY_VALUE(latest_institutions) AS latest_institutions,
    ANY_VALUE(summary_stats) AS summary_stats,
    ANY_VALUE(ids) AS ids,
    FLATTEN(ARRAY_AGG(works)) as relevant_works,
    -- Basic metrics
    SUM(total_citations_in_topic) AS sum_citations,
    SUM(works_count_in_topic) AS sum_works_count,
    MAX(latest_publication_date_in_topic) AS latest_publication_date,
    
    -- Topic-weighted metrics with ceiling
    LEAST(
      SUM(total_citations_in_topic * tt.topic_relevance_score) / SUM(tt.topic_relevance_score), 
      10000.0
    ) AS weighted_citations,
    SUM(tt.topic_relevance_score) / COUNT(*) AS avg_topic_relevance,
    AVG(topic_share_value) AS avg_topic_share_value,
    
    -- Works count metric (normalized)
    SUM(works_count_in_topic * tt.topic_relevance_score) / SUM(tt.topic_relevance_score) AS weighted_works_count,
    
    -- 2yr mean citedness (normalized, capped at 10)
    LEAST(COALESCE(ANY_VALUE(summary_stats."2yr_mean_citedness"), 0.0), 10.0) / 10.0 AS normalized_mean_citedness,
    
    -- Recency score (0-1, where 1 = published today, decays over 5 years)
    CASE 
      WHEN MAX(latest_publication_date_in_topic) IS NULL THEN 0.0
      ELSE GREATEST(0.0, 1.0 - (CURRENT_DATE - MAX(latest_publication_date_in_topic))::DOUBLE / 1825.0)
    END AS recency_score
    
  FROM read_parquet(
    '${parquetPath}/*/*.parquet',
    hive_partitioning = true,
    hive_types = {'topic_id': VARCHAR}
  ) atr
  INNER JOIN top_topics tt ON atr.topic_id = tt.topic_id
  GROUP BY author_id
  HAVING MAX(latest_publication_date_in_topic) >= CURRENT_DATE - INTERVAL '15 years'
),
-- Calculate normalization factors once
normalization_factors AS (
  SELECT 
    MAX(weighted_citations) AS max_weighted_citations,
    MAX(weighted_works_count) AS max_weighted_works_count
  FROM author_topics_result
  WHERE weighted_citations > 0
),
-- Final ranking using pre-calculated max values
final_ranking AS (
  SELECT 
    atr.*,
    (
      0.40 * (atr.weighted_citations / NULLIF(nf.max_weighted_citations, 0)) +
      0.20 * atr.normalized_mean_citedness +
      0.15 * (atr.weighted_works_count / NULLIF(nf.max_weighted_works_count, 0)) +
      0.10 * atr.recency_score +
      0.15 * atr.avg_topic_relevance
    ) AS composite_score
  FROM author_topics_result atr
  CROSS JOIN normalization_factors nf
  WHERE atr.weighted_citations > 0
)
SELECT
  author_id as id,
  display_name,
  ids,
  struct_pack(
    h_index := summary_stats.h_index,
    two_year_mean_citedness := summary_stats."2yr_mean_citedness",
    i10_index := summary_stats.i10_index
  ) as summary_stats,
  latest_institutions,
  len(relevant_works) as len_works,
  list_transform(
    relevant_works,
    work -> struct_pack(
      id := work.id,
      display_name := work.display_name,
      publication_date := work.publication_date,
      doi := work.doi,
      oa_url := work.oa_url,
      fwci := work.fwci,
      cited_by_count := work.cited_by_count,
      authorships := work.authorships
    )
  ) as works_list
FROM final_ranking
ORDER BY composite_score DESC
LIMIT 20;
`;

export async function rankAuthors(
  conn: DuckDBConnection,
  queryContent: string
) {
  const queryEmbedding = await generateEmbedding(queryContent);
  const prepared = await conn.prepare(authorsQuery);
  prepared.bind({
    query_embedding: arrayValue(queryEmbedding),
  });

  const reader = await prepared.runAndReadAll();
  const rows = reader.getRowObjectsJson();

  return rows as AuthorRankingResult[];
}
