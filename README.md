# PLMBot MVP Prototype

This repository implements a minimal local prototype for PLM-style CRUD + relational retrieval:

`CLI -> LangChain agent -> typed tools -> services -> SQLAlchemy ORM -> PostgreSQL`

## Scope (MVP)
- Component CRUD with guarded mutations
- Flat BOM traversal (`get_bom`, `where_used`)
- Read retrieval with exact + `ILIKE` fallback
- Tool-backed answers and visible CLI traces

## Quickstart
1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start Postgres:
   ```bash
   docker compose up -d db
   ```
3. Run migrations:
   ```bash
   docker compose run --rm app alembic upgrade head
   ```
4. Seed data:
   ```bash
   docker compose run --rm app python -m app.seed.seed_runner
   ```
5. Start CLI:
   ```bash
   docker compose run --rm app python -m app.cli
   ```

## Project Layout
See the `app/` tree for agent, tools, services, db, seed, and tests.
