import { $ } from "bun";

const DB_PATH = process.env.DB_PATH;
const DENORM_PARQUET_PATH = process.env.DENORM_PARQUET_PATH;

if (!DB_PATH) {
  throw new Error("DB_PATH environment variable is required");
}

if (!DENORM_PARQUET_PATH) {
  throw new Error("DENORM_PARQUET_PATH environment variable is required");
}

console.log("Uploading DuckDB database...");
console.log(`  From: ${DB_PATH}`);
console.log(`  To: /data/openalex.duckdb`);

await $`fly ssh sftp put ${DB_PATH} /data/openalex.duckdb`;

console.log("\nUploading parquet files...");
console.log(`  From: ${DENORM_PARQUET_PATH}`);
console.log(`  To: /data/parquet`);

await $`fly ssh sftp put -R ${DENORM_PARQUET_PATH} /data/parquet`;

console.log("\nUpload complete!");
