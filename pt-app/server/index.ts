import { Elysia, sse, t } from "elysia";
import { cors } from "@elysiajs/cors";
import { DuckDBConnection, DuckDBInstance } from "@duckdb/node-api";
import { open, RootDatabase } from "lmdb";
import { rankAuthors } from "./db";
import { generateAuthorSummary } from "./ai";
import { AuthorRankingResult } from "./types";
import { readOrcidRecord } from "./orcid";
import { getCachedValue, putCachedValue } from "./cache";

async function getDuckDBInstance() {
  const path = process.env.DB_PATH;
  if (!path) {
    throw new Error(
      "DB_PATH environment variable is not set. " +
      "DuckDB features require this to be configured."
    );
  }
  const instance = await DuckDBInstance.create(path, {
    access_mode: "READ_ONLY",
  });
  return instance;
}

async function getDuckDBConnection() {
  const instance = await getDuckDBInstance();
  const connection = await DuckDBConnection.create(instance);
  return connection;
}

// Lazy singleton for DuckDB connection
let connectionPromise: Promise<DuckDBConnection> | null = null;

function getConnection(): Promise<DuckDBConnection> {
  if (!connectionPromise) {
    connectionPromise = getDuckDBConnection();
  }
  return connectionPromise;
}

async function getQueryAuthors(
  queryContent: string,
  duckDb: DuckDBConnection
) {
  const cachedAuthors = getCachedValue<AuthorRankingResult[]>(queryContent);
  if (cachedAuthors) {
    return cachedAuthors;
  }

  const freshAuthors = await rankAuthors(duckDb, queryContent);
  await putCachedValue(queryContent, freshAuthors);
  return freshAuthors;
}

async function getAuthorSummary(
  author: AuthorRankingResult,
  queryContent: string
) {
  const cacheKey = `summary_${author.id}_${queryContent}`;
  const cachedSummary = getCachedValue<string>(cacheKey);
  if (cachedSummary) {
    return cachedSummary;
  }

  const freshSummary = await generateAuthorSummary(author, queryContent);
  await putCachedValue(cacheKey, freshSummary);
  return freshSummary;
}

async function* generateAuthorSummariesInParallel(
  authors: AuthorRankingResult[],
  searchQuery: string,
) {
  // Start all summary generation promises in parallel
  const summaryPromises = authors.map((author) => ({
    authorId: author.id,
    promise: getAuthorSummary(author, searchQuery),
  }));

  const pendingPromises = [...summaryPromises];

  // Yield results as they complete using Promise.race
  while (pendingPromises.length > 0) {
    const { authorId, summary } = await Promise.race(
      pendingPromises.map(async ({ authorId, promise }) => ({
        authorId,
        summary: await promise,
      }))
    );

    // Remove the completed promise from pending list
    const completedIndex = pendingPromises.findIndex(p => p.authorId === authorId);
    if (completedIndex !== -1) {
      pendingPromises.splice(completedIndex, 1);
    }

    yield {
      authorId,
      summary,
    };
  }
}

const app = new Elysia()
  .use(cors())
  .get("/", () => "Papertrail API")
  .get(
    "/query",
    async function* (ctx) {
      const db = await getConnection();
      const searchQuery = ctx.query.content;
      const authors = await getQueryAuthors(searchQuery, db);
      
      // Process each author's works - sort by cited count desc and take top 5
      const processedAuthors = authors.map(author => ({
        ...author,
        works_list: [...author.works_list]
          .sort((a, b) => b.cited_by_count - a.cited_by_count)
          .slice(0, 5)
      }));
      
      yield sse({
        id: "1",
        event: "authors",
        data: processedAuthors,
      });

      // Generate author summaries in parallel and stream as they complete
      for await (const { authorId, summary } of generateAuthorSummariesInParallel(processedAuthors, searchQuery)) {
        yield sse({
          id: `summary-${authorId}`,
          event: "author_summary",
          data: {
            authorId,
            summary,
          },
        });
      }
    },
    {
      query: t.Object({
        content: t.String(),
      }),
    }
  )
  .get("/test-duckdb", async () => {
    const connection = await getConnection();
    connection.run("from test_all_types()");

    return "OK";
  })
  .get(
    "/orcid/:id",
    async (ctx) => {
      const id = ctx.params.id;
      const decodedId = decodeURIComponent(id);
      const record = await readOrcidRecord(decodedId);
      return record;
    },
  );

app.listen(8888);
console.log("Server is running on http://localhost:8888");

export type App = typeof app;
