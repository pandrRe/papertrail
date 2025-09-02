import { arrayValue, DuckDBConnection } from "@duckdb/node-api";
import { generateEmbedding } from "./ai";
import { AuthorRankingResult } from "./types";

const authorsQuery = `\
WITH 
-- Step 1: Get top K topics using HNSW index for fast similarity search
top_topics AS (
  SELECT
    id AS topic_id,
    display_name AS topic_name,
    (array_cosine_similarity(embedding, $query_embedding::FLOAT[768]) + 1) / 2 AS normalized_score,
    ROW_NUMBER() OVER (ORDER BY array_cosine_similarity(embedding, $query_embedding::FLOAT[768]) DESC) AS topic_rank
  FROM topics
  ORDER BY array_cosine_similarity(embedding, $query_embedding::FLOAT[768]) DESC
  LIMIT 5
),
-- Step 1b: Apply exponential weighting
weighted_topics AS (
  SELECT
    topic_id,
    topic_name,
    normalized_score,
    topic_rank,
    normalized_score * EXP(-0.5 * (topic_rank - 1)) AS weighted_score
  FROM top_topics
),
-- Step 2a: Pre-filter author_topics before joining (using index on topic_id)
relevant_authors_pre AS (
  SELECT 
    att.author_id,
    att.topic_id,
    att."value" AS topic_value
  FROM author_topics att
  WHERE att.topic_id IN (SELECT topic_id FROM weighted_topics)
),
-- Step 2b: Now join with weighted_topics for additional fields
relevant_authors AS (
  SELECT 
    rap.author_id,
    rap.topic_id,
    rap.topic_value,
    wt.topic_name,
    wt.normalized_score AS topic_similarity_score,
    wt.weighted_score AS topic_weighted_score,
    wt.topic_rank
  FROM relevant_authors_pre rap
  INNER JOIN weighted_topics wt ON rap.topic_id = wt.topic_id
),
-- Step 3: Get unique authors first (reduces downstream processing)
unique_authors AS (
  SELECT DISTINCT author_id
  FROM relevant_authors
),
-- Step 4: Get works more efficiently using primary_topic_id index
relevant_works AS (
  SELECT
    w.id,
    w.display_name,
    w.publication_date,
    w.primary_topic_id,
    w.fwci,
    w.cited_by_count
  FROM weighted_topics wt
  INNER JOIN works w ON w.primary_topic_id = wt.topic_id
  WHERE w.publication_date >= CURRENT_DATE - INTERVAL '10 years'  -- Early filter for recency
),
-- Step 5: Get authorships only for relevant works and authors
relevant_authorships AS (
  SELECT 
    ash.author_id,
    ash.work_id,
    ash.author_position,
    rw.display_name AS work_display_name,
    rw.publication_date,
    rw.primary_topic_id,
    rw.fwci,
    rw.cited_by_count
  FROM unique_authors ua
  INNER JOIN authorships ash ON ash.author_id = ua.author_id
  INNER JOIN relevant_works rw ON rw.id = ash.work_id
),
-- Step 6: Build authorship arrays per work
work_authorships AS (
  SELECT
    rash.work_id,
    rash.author_id AS main_author_id,
    ARRAY_AGG(
      STRUCT_PACK(
        display_name := a.display_name,
        author_position := ash2.author_position
      ) ORDER BY ash2.author_position
    ) AS authorships
  FROM relevant_authorships rash
  INNER JOIN authorships ash2 ON ash2.work_id = rash.work_id
  INNER JOIN authors a ON a.id = ash2.author_id
  GROUP BY rash.work_id, rash.author_id
),
-- Step 7: Combine work data with authorships
author_works AS (
  SELECT 
    rash.author_id,
    rash.work_id,
    rash.work_display_name,
    rash.publication_date,
    rash.primary_topic_id,
    rash.fwci,
    rash.cited_by_count,
    wa.authorships,
    wt.topic_name,
    wt.normalized_score AS topic_similarity_score,
    wt.weighted_score AS topic_weighted_score,
    EXP(-0.2 * GREATEST(0, EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM rash.publication_date))) AS recency_score
  FROM relevant_authorships rash
  INNER JOIN weighted_topics wt ON wt.topic_id = rash.primary_topic_id
  INNER JOIN work_authorships wa ON wa.work_id = rash.work_id AND wa.main_author_id = rash.author_id
),
-- Step 8: Calculate author metrics
author_metrics AS (
  SELECT 
    ra.author_id,
    COUNT(DISTINCT ra.topic_id) AS num_topics_covered,
    SUM(ra.topic_value * ra.topic_weighted_score) AS weighted_topic_value,
    AVG(ra.topic_value) AS avg_topic_value,
    LIST(DISTINCT ra.topic_rank ORDER BY ra.topic_rank) AS topic_ranks_covered,
    COALESCE(
      LIST(
        STRUCT_PACK(
          work_id := aw.work_id,
          display_name := aw.work_display_name,
          publication_date := aw.publication_date,
          topic := aw.topic_name,
          fwci := aw.fwci,
          cited_by_count := aw.cited_by_count,
          authorships := aw.authorships
        ) ORDER BY aw.publication_date DESC
      ) FILTER (WHERE aw.work_id IS NOT NULL),
      []
    ) AS works_list,
    COALESCE(AVG(aw.fwci), 0) AS avg_fwci,
    COALESCE(SUM(aw.fwci), 0) AS total_fwci,
    COUNT(DISTINCT aw.work_id) AS work_count,
    COALESCE(AVG(aw.recency_score), 0) AS avg_recency_score,
    COALESCE(MAX(aw.publication_date), DATE '1900-01-01') AS most_recent_publication,
    FIRST(aw.work_id ORDER BY aw.publication_date DESC) AS most_recent_work_id
  FROM relevant_authors ra
  LEFT JOIN author_works aw ON ra.author_id = aw.author_id 
    AND ra.topic_id = aw.primary_topic_id
  GROUP BY ra.author_id
  HAVING COUNT(DISTINCT aw.work_id) >= 2  -- Early filter
),
-- Step 9a: Pre-filter work_institutions before joining with institutions
relevant_work_institutions_pre AS (
  SELECT 
    wi.work_id,
    wi.author_id,
    wi.institution_id
  FROM author_metrics am
  INNER JOIN work_institutions wi ON wi.work_id = am.most_recent_work_id 
    AND wi.author_id = am.author_id
  WHERE am.most_recent_work_id IS NOT NULL
),
-- Step 9b: Now join with institutions for full data
relevant_work_institutions AS (
  SELECT 
    rwip.work_id,
    rwip.author_id,
    i.id,
    i.ror,
    i.display_name,
    i.ids,
    i.country_code,
    i.geo,
    i.homepage_url,
    i.image_url,
    i.image_thumbnail_url,
    i.cited_by_count
  FROM relevant_work_institutions_pre rwip
  INNER JOIN institutions i ON rwip.institution_id = i.id
),
-- Step 10: Combine everything with calculated scores
author_with_institution AS (
  SELECT 
    am.*,
    a.id,
    a.display_name,
    a.summary_stats,
    a.ids,
    FIRST(
      CASE 
        WHEN rwi.id IS NOT NULL THEN
          STRUCT_PACK(
            id := rwi.id,
            ror := rwi.ror,
            display_name := rwi.display_name,
            ids := rwi.ids,
            country_code := rwi.country_code,
            geo := rwi.geo,
            homepage_url := rwi.homepage_url,
            image_url := rwi.image_url,
            image_thumbnail_url := rwi.image_thumbnail_url
          )
        ELSE NULL
      END ORDER BY rwi.cited_by_count DESC NULLS LAST
    ) AS latest_institution,
    (
      0.1 * (am.num_topics_covered::DOUBLE / 5.0) +
      0.2 * LEAST(am.weighted_topic_value, 1.0) +
      0.3 * LEAST(am.avg_fwci / 2.0, 1.0) +
      0.2 * LEAST(am.work_count / 20.0, 1.0) +
      0.2 * am.avg_recency_score
    ) AS ranking_score,
    ROUND(LEAST(am.work_count / 10.0, 1.0), 4) AS productivity_score,
    DATE_DIFF('day', am.most_recent_publication, CURRENT_DATE) AS days_since_last_pub
  FROM author_metrics am
  INNER JOIN authors a ON am.author_id = a.id
  LEFT JOIN relevant_work_institutions rwi ON rwi.work_id = am.most_recent_work_id 
    AND rwi.author_id = am.author_id
  WHERE DATE_DIFF('day', am.most_recent_publication, CURRENT_DATE) <= 365 * 10
  GROUP BY 
    am.author_id, am.num_topics_covered, am.weighted_topic_value, 
    am.avg_topic_value, am.topic_ranks_covered, am.works_list,
    am.avg_fwci, am.total_fwci, am.work_count, am.avg_recency_score,
    am.most_recent_publication, am.most_recent_work_id,
    a.id, a.display_name, a.summary_stats, a.ids
)
-- Final output
SELECT 
  ROW_NUMBER() OVER (ORDER BY ranking_score DESC) AS rank,
  id,
  display_name,
  ids,
  struct_pack(
    h_index := summary_stats.h_index,
    two_year_mean_citedness := summary_stats."2yr_mean_citedness",
    i10_index := summary_stats.i10_index
  ) as summary_stats,
  latest_institution,
  works_list
FROM author_with_institution
ORDER BY ranking_score DESC
LIMIT 10;
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
