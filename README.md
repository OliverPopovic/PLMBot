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

## CLI Usage
The CLI now accepts plain-English requests or explicit commands.

Examples:
```text
find R-14
list components
list assemblies
show me the BOM for A-1000
list all components inside assembly A-1000
where is C-102 used?
create {"component_code":"IC-555","name":"Timer IC","component_type":"ic"}
update IC-555 {"description":"555 timer"}
delete IC-555
```

Behavior:
- Read operations execute immediately after the app shows the interpreted instruction.
- Write operations show the normalized instruction and require `y` or `yes` confirmation.
- Unsupported or ambiguous requests are rejected with a clarification or safety message.

## Project Layout
See the `app/` tree for agent, tools, services, db, seed, and tests.
