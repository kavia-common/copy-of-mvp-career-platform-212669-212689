# CareerPlatformBackendAPI

This backend is built with FastAPI. It supports PostgreSQL (async via `asyncpg`) if configured, and falls back to SQLite (async via `aiosqlite`) for local/MVP use.

## Database Configuration

- Preferred (PostgreSQL async):
  - Set one of:
    - `DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME`
    - `POSTGRES_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME` (driver normalized automatically)
    - Discrete vars:
      - `POSTGRES_USER=...`
      - `POSTGRES_PASSWORD=...`
      - `POSTGRES_DB=...`
      - `POSTGRES_HOST=localhost` (default)
      - `POSTGRES_PORT=5432` (default)
- Fallback (SQLite async):
  - `DATABASE_URL=sqlite+aiosqlite:///./data/app.db`

Tables are created at startup using `Base.metadata.create_all` (no Alembic migrations in the MVP).

## Environment

Copy `.env.example` to `.env` and adjust as necessary. Common entries:

```
# PostgreSQL (recommended for integration)
# DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
# or:
# POSTGRES_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
# or:
# POSTGRES_USER=...
# POSTGRES_PASSWORD=...
# POSTGRES_DB=...
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432

# Optional helper to enable seeding endpoints
ALLOW_SEED_ENDPOINT=true

# SQLite fallback
# DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

## Getting Started

1. Create a virtual environment and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the API (example):
   ```
   uvicorn src.api.main:app --reload --port 3001
   ```

3. Visit API docs:
   - Swagger UI: http://localhost:3001/docs
   - OpenAPI JSON: http://localhost:3001/openapi.json

## Test the DB

Simple CRUD endpoints are provided to validate data access:

- Users:
  - `POST /api/v1/users` – create a user
  - `GET /api/v1/users` – list users (supports `?q=` search)
  - `GET /api/v1/users/{user_id}` – get a user by ID

- Roles:
  - `POST /api/v1/roles` – create a role
  - `GET /api/v1/roles` – list roles (supports `?q=` search)
  - `POST /api/v1/roles/seed` – insert a sample role (requires `ALLOW_SEED_ENDPOINT=true`)

### Quick Test (Roles)

Seed a sample role (if enabled):
```
curl -X POST http://localhost:3001/api/v1/roles/seed
```

Create a role:
```
curl -s -X POST http://localhost:3001/api/v1/roles \
  -H "Content-Type: application/json" \
  -d '{"name": "Chief Architect", "description": "Owns system architecture", "metadata": {"domain":"Platform"}, "version":"2025.1", "source":"manual"}'
```

List roles:
```
curl -s http://localhost:3001/api/v1/roles | jq .
```

## Notes

- The `data/` directory is created automatically for SQLite and `*.db` files are ignored by `.gitignore`.
- For production or multi-process deployments, ensure file permissions for `data/` are correct.
