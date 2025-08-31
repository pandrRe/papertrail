import { Elysia } from "elysia";
import { DuckDBConnection, DuckDBInstance } from "@duckdb/node-api";

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

const app = new Elysia()
  .get("/", () => "Papertrail API")
  .decorate("db", connection)
  .get("/test-duckdb", async () => {
    // Create DuckDB connection
    connection.run("from test_all_types()");

    return "OK";
  });

app.listen(8888);
console.log("Server is running on http://localhost:8888");
