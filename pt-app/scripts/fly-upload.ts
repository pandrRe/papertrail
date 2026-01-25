import { $ } from "bun";
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";

const DB_PATH = process.env.DB_PATH;
const DENORM_PARQUET_PATH = process.env.DENORM_PARQUET_PATH;

if (!DB_PATH) {
  throw new Error("DB_PATH environment variable is required");
}

if (!DENORM_PARQUET_PATH) {
  throw new Error("DENORM_PARQUET_PATH environment variable is required");
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024)
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function formatElapsedTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes === 0) return `${remainingSeconds}s`;
  return `${minutes}m ${remainingSeconds}s`;
}

async function getFileSize(path: string): Promise<number> {
  const fileStat = await stat(path);
  return fileStat.size;
}

async function getDirectoryInfo(
  path: string
): Promise<{ totalSize: number; fileCount: number }> {
  let totalSize = 0;
  let fileCount = 0;

  const entries = await readdir(path, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(path, entry.name);
    if (entry.isFile()) {
      const fileStat = await stat(fullPath);
      totalSize += fileStat.size;
      fileCount++;
    } else if (entry.isDirectory()) {
      const subInfo = await getDirectoryInfo(fullPath);
      totalSize += subInfo.totalSize;
      fileCount += subInfo.fileCount;
    }
  }

  return { totalSize, fileCount };
}

console.log("Cleaning up existing files...");
await $`fly ssh console -C "rm -f /data/openalex.duckdb"`;
await $`fly ssh console -C "rm -rf /data/parquet"`;

const dbSize = await getFileSize(DB_PATH);
console.log("\nUploading DuckDB database...");
console.log(`  From: ${DB_PATH} (${formatBytes(dbSize)})`);
console.log(`  To: /data/openalex.duckdb`);

let startTime = Date.now();
await $`fly ssh sftp put --verbose ${DB_PATH} /data/openalex.duckdb`;
console.log(`  Completed in ${formatElapsedTime(Date.now() - startTime)}`);

const parquetInfo = await getDirectoryInfo(DENORM_PARQUET_PATH);
console.log("\nUploading parquet files...");
console.log(
  `  From: ${DENORM_PARQUET_PATH} (${parquetInfo.fileCount} files, ${formatBytes(parquetInfo.totalSize)} total)`
);
console.log(`  To: /data/parquet`);

startTime = Date.now();
await $`fly ssh sftp put --verbose -R ${DENORM_PARQUET_PATH} /data/parquet`;
console.log(`  Completed in ${formatElapsedTime(Date.now() - startTime)}`);

console.log("\nUpload complete!");
