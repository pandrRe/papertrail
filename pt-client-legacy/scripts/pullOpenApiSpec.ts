const path = `${import.meta.env.PAPERTRAIL_API_URL}/openapi.json`;
const output = "./openapi.json";

const response = await fetch(path);
if (!response.ok) {
  throw new Error(`❌ Failed to fetch OpenAPI spec from ${path}`);
}

const data = await response.text();
await Bun.write(output, data);

console.log(`✅ Wrote OpenAPI spec to ${output}`);

export {};
