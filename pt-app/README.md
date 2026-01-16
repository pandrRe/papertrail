# pt-app

Elysia/Bun API server for Papertrail.

## Deploying to Fly.io

### Prerequisites

- [Fly CLI](https://fly.io/docs/flyctl/install/) installed and authenticated (`fly auth login`)
- Local data files configured in `.env.server.local`:
  - `DB_PATH` - path to OpenAlex DuckDB database
  - `DENORM_PARQUET_PATH` - path to denormalized parquet files

### 1. Create the app

```bash
cd pt-app
fly launch --no-deploy
```

### 2. Set secrets

```bash
fly secrets set GEMINI_API_KEY=<your-key>
fly secrets set ORCID_CLIENT_ID=<your-id>
fly secrets set ORCID_CLIENT_SECRET=<your-secret>
```

### 3. Deploy

```bash
fly deploy
```

This creates a 150GB volume on first deploy (for ~110GB of data).

### 4. Upload data

```bash
bun run fly:upload
```

This reads paths from `.env.server.local` and uploads:
- DuckDB database → `/data/openalex.duckdb`
- Parquet files → `/data/parquet`

### 5. Verify

```bash
# Check files on the container
fly ssh console -C "ls -la /data/"

# Test the API
curl https://pt-app-server.fly.dev/
```

## Configuration

The VM is configured with:
- **Region**: GRU (São Paulo)
- **Memory**: 8GB
- **CPUs**: 4 shared
- **Volume**: 150GB
- **Scale to zero**: Yes (stops when idle, starts on request)

## Local Development

```bash
# Start the server
bun run server:dev
```
