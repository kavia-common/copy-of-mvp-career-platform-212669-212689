# CareerPlatformBackendAPI

This backend is built with FastAPI. It now defaults to SQLite (async via `aiosqlite`) for local/MVP use to simplify setup and avoid external DB dependencies. PostgreSQL-specific configuration is disabled in this migration step.

## Database Configuration

- Default (SQLite async, recommended for local/dev and MVP):
  - Uses `sqlite+aiosqlite:///./data/app.db`
  - Tables are created automatically at startup using `Base.metadata.create_all`.
  - The `data/` directory is created on demand.

- Optional override (SQLite only during this migration):
  - Set `DATABASE_URL` to a SQLite URL. Examples:
    - File DB:
      - `DATABASE_URL=sqlite+aiosqlite:///./data/app.db`
      - `DATABASE_URL=sqlite+aiosqlite:///./my_local.db`
    - In-memory (ephemeral):
      - `DATABASE_URL=sqlite+aiosqlite:///:memory:`
    - If you supply a `sqlite://` URL, it will be normalized to `sqlite+aiosqlite://` automatically.

- PostgreSQL:
  - PostgreSQL environment variables (`POSTGRES_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.) are intentionally ignored in this migration to prevent accidental connections to unavailable instances.
  - The `asyncpg` dependency is removed. If you later want to re-enable PostgreSQL async support, you will need to:
    1) Add `asyncpg` back to `requirements.txt`
    2) Provide a suitable async URL (e.g., `postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME`)
    3) Update configuration to honor Postgres env vars again.

## Environment

Copy `.env.example` to `.env` and adjust as necessary. Common entries:

```
# Optional helper to enable seeding endpoints
ALLOW_SEED_ENDPOINT=true

# Optional: toggle email validation strictness for auth & user schemas.
# When false (default), email validation is relaxed and only checks for the presence of '@'.
# When true, strict RFC-style validation is enforced using the email_validator package.
STRICT_EMAIL_VALIDATION=false

# Optional: override default SQLite path
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

## Auth (Updated)

- Register:
  - `POST /api/v1/auth/register`
  - Payload: `{ "email": "<email>", "name": "<name>", "password": "<password>" }`
  - Behavior: Password is never stored in plaintext; it is salted and hashed (PBKDF2). The response never includes the password.

- Login:
  - `POST /api/v1/auth/login`
  - Payload: `{ "email": "<email>", "password": "<password>" }`
  - Behavior: Validates the supplied password and returns a JWT token on success; returns 401 on invalid credentials and 400 if required fields are missing.

- Logout:
  - `POST /api/v1/auth/logout` (and aliases `/api/v1/login`, `/api/v1/logout` are supported)

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

- SQLite is the default for local/MVP. No external DB is required.
- For production or multi-process deployments, ensure file permissions for `data/` are correct.
- PostgreSQL support can be reinstated later by reintroducing the `asyncpg` dependency and re-enabling Postgres env handling in `src/core/config.py`.
