# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server (pt-server/)
- **Start development server**: `uv run fastapi dev`
- **Dependencies**: Managed with `uv` - Python package manager

### Client (pt-client/)  
- **Start development server**: `bun run start` (runs on port 3000)
- **Build for production**: `bun run build && tsc`
- **Run tests**: `bun run test` (uses Vitest)
- **Pull OpenAPI spec**: `bun run schema:pull`  
- **Generate API client**: `bun run schema:generate` (generates from openapi.json using Kubb)
- **Dependencies**: Managed with `bun`

### API Schema Generation
The client uses Kubb to generate TypeScript types and React Query hooks from the FastAPI OpenAPI schema. After making API changes:
1. Run `bun run schema:pull` to fetch latest OpenAPI spec
2. Run `bun run schema:generate` to regenerate client code in `src/lib/contracts/`

## Architecture Overview

### Server Architecture (Python/FastAPI)
- **Framework**: FastAPI with SSE (Server-Sent Events) for streaming responses
- **Database**: SQLite with SQLAlchemy ORM, uses aiosqlite for async operations
- **Caching**: Built-in cache system using database for Google Scholar API responses and AI summaries
- **AI Integration**: 
  - Anthropic Claude API for generating author publication summaries (in Portuguese)
  - SentenceTransformers for semantic search and publication ranking
- **External APIs**: Google Scholar via `scholarly` library
- **Main modules**:
  - `app/main.py`: FastAPI app setup with CORS, streaming endpoints
  - `app/sources/scholarly.py`: Google Scholar search integration with caching and AI summarization
  - `app/internal/db.py`: Database models and caching infrastructure
  - `app/dependencies.py`: Dependency injection for SentenceTransformer model

### Client Architecture (React/TypeScript)
- **Framework**: React with TanStack Router for file-based routing  
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: TanStack Query for server state, no global client state
- **Type Safety**: Full TypeScript with auto-generated API types from OpenAPI schema
- **Build Tool**: Vite with Bun as package manager
- **Key features**:
  - Real-time search results via SSE streaming
  - Semantic search interface for academic authors and publications
  - Portuguese language AI-generated author summaries

### Data Flow
1. User enters search query in React client
2. Client sends request to `/search` endpoint with SSE
3. Server performs parallel searches (authors by keywords, publications by query)
4. Results are cached and streamed back as they arrive
5. Server fills author details, ranks publications by relevance, generates AI summaries
6. Client receives and displays updates in real-time

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, aiosqlite, scholarly, anthropic, sentence-transformers
- **Frontend**: React, TanStack Router, TanStack Query, Tailwind CSS, Vite
- **Type Generation**: Kubb for OpenAPI → TypeScript conversion
- **Package Management**: uv (Python), bun (Node.js)

## Development Workflow

1. **Making API Changes**: 
   - Modify FastAPI endpoints in `pt-server/`
   - Restart server with `uv run fastapi dev`
   - In client, run `bun run schema:pull` then `bun run schema:generate`
   - Generated types/hooks will be in `src/lib/contracts/`

2. **Database Changes**:
   - Models are in `pt-server/app/internal/db.py`
   - Database file: `pt-server/db/local.db`

3. **Adding UI Components**:
   - Use shadcn/ui: `pnpx shadcn@canary add <component>`
   - Components go in `src/components/ui/`