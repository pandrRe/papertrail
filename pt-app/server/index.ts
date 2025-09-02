import { Elysia, sse, t } from "elysia";
import { cors } from "@elysiajs/cors";
import { DuckDBConnection, DuckDBInstance } from "@duckdb/node-api";
import { open, RootDatabase } from "lmdb";
import { rankAuthors } from "./db";
import { generateAuthorSummary } from "./ai";
import { AuthorRankingResult } from "./types";

async function getDuckDBInstance() {
  const path = process.env.DB_PATH;
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

const connection = await getDuckDBConnection();
const lmdb = open({
  path: process.env.LMDB_PATH || "./.data/lmdb",
  compression: true,
});

type CacheEntry<T> = {
  timestamp: number;
  content: T;
};
const CACHE_TTL = 1000 * 60 * 24; // 24 hours

function getCachedValue<T>(key: string): T | undefined {
  const entry = lmdb.get(key) as CacheEntry<T> | undefined;
  if (entry) {
    const isExpired = Date.now() - entry.timestamp > CACHE_TTL;
    if (!isExpired) {
      return entry.content;
    }
  }
  return undefined;
}

async function putCachedValue<T>(key: string, content: T) {
  const entry: CacheEntry<T> = {
    timestamp: Date.now(),
    content,
  };
  await lmdb.put(key, entry);
}

async function getQueryAuthors(
  queryContent: string,
  duckDb: DuckDBConnection,
  lmdb: RootDatabase
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

async function wait(timeout: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeout));
}

const app = new Elysia()
  .use(cors())
  .get("/", () => "Papertrail API")
  .decorate("db", connection)
  .decorate("lmdb", lmdb)
  .get(
    "/query",
    async function* (ctx) {
      const searchQuery = ctx.query.content;
      const authors = await getQueryAuthors(searchQuery, ctx.db, ctx.lmdb);
      yield sse({
        id: "1",
        event: "authors",
        data: authors,
      });

      await wait(10);

      for (let i = 0; i < authors.length; i++) {
        const author = authors[i];
        const summary = await getAuthorSummary(author, searchQuery);
        yield sse({
          id: `summary-${author.id}`,
          event: "author_summary",
          data: {
            authorId: author.id,
            summary,
          },
        });
        await wait(5);
      }
    },
    {
      query: t.Object({
        content: t.String(),
      }),
    }
  )
  .get("/test-duckdb", async () => {
    // Create DuckDB connection
    connection.run("from test_all_types()");

    return "OK";
  });

app.listen(8888);
console.log("Server is running on http://localhost:8888");

export type App = typeof app;
