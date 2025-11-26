# CareerPlatformBackendAPI

This backend is built with FastAPI and configured to use SQLite (async via `aiosqlite`) for the MVP.

## SQLite Configuration

- Engine: `sqlite+aiosqlite`
- Default DB URL: `sqlite+aiosqlite:///./data/app.db`
- Session: Async SQLAlchemy (`AsyncSession`)
- Migrations: Not configured for MVP. Tables are created at startup (`Base.metadata.create_all`).

## Environment

Copy `.env.example` to `.env` and adjust as necessary:

```
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

Previous PostgreSQL environment variables are no longer used after migration.

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

A simple `Users` CRUD is provided to validate SQLite data access:

- `POST /api/v1/users` – create a user
- `GET /api/v1/users` – list users (supports `?q=` search)
- `GET /api/v1/users/{user_id}` – get a user by ID

## Notes

- The `data/` directory is created automatically and `*.db` files are ignored by `.gitignore`.
- For production or multi-process deployments, ensure file permissions for `data/` are correct.
