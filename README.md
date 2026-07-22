# OmniRAG

OmniRAG is a temporal knowledge graph system for organizational and academic memory. It connects GitHub activity, Slack decisions, and uploaded documents into a queryable intelligence layer with citations, graph-derived confidence, and temporal history.

This repository follows the locked project authority in:

- `docs/OmniRAG-Blueprint-v2.md`
- `docs/industrial-vibe-coding-rules-v4.md`

Do not change architecture, stack, phase order, or engineering rules without resolving the conflict against those documents first.

## Locked Stack

- Backend: Python 3.12 + FastAPI
- Graph database: Neo4j
- Document database and vector search: MongoDB + MongoDB Atlas Vector Search
- Queue/cache/pubsub: Redis 7
- Local LLM: Ollama `llama3`
- LLM provider: Groq LLaMA 3.1 8B and 70B
- Agent orchestration: LangGraph
- Frontend: React + TypeScript + Tailwind + react-force-graph
- Local runtime: Docker + Docker Compose
- CI/CD: GitHub Actions

## Phase 2 Status

This repository has completed Phase 2: Backend Skeleton.

Implemented so far:

- Phase 1 foundation (Docker Compose, Dockerfile, CI skeleton, Makefile)
- FastAPI app factory with CORS, security headers, correlation-ID
  middleware, and standard-envelope error handling
- Pydantic Settings singleton — validates all required env vars on
  startup, fails fast with a clear error if any are missing
- Structured logging (structlog) — every log entry carries
  `correlation_id`, `service`, `level`, `timestamp`, `event`
- All 18 locked endpoints from Blueprint 2.4, each returning the
  standard response envelope (`success`, `data`, `error`, `meta`)
- `GET /api/v1/health` reporting per-service status (`mongodb`, `neo4j`,
  `redis`, `ollama`) — real connectivity checks land in Phase 3
- Missing/invalid request bodies return `400 VALIDATION_ERROR` with
  field-level detail, matching the Blueprint 2.4 contract exactly

Not yet built (explicitly deferred, not neglected):

- JWT auth enforcement / `401` on invalid token — Phase 4
- Rate limiting — Phase 4
- Real database connectivity in `/api/v1/health` and repositories — Phase 3

## Local Development

1. Copy `.env.example` to `.env`.
2. Fill required secrets and service URLs.
3. Start the local stack:

```bash
make dev
```

4. Verify the API:

```bash
curl http://localhost:3001/api/v1/health
```

Expected Phase 2 response:

```json
{
  "status": "starting",
  "services": {
    "mongodb": "starting",
    "neo4j": "starting",
    "redis": "starting",
    "ollama": "starting"
  }
}
```

## Commands

```bash
make dev
make test
make lint
make seed
make build
make pull-models
```

`make seed` is reserved for Phase 3 and currently fails intentionally until the database seed script exists.
