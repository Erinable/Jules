# Jules

Jules is a full-stack AI code generation platform. The current repository contains a
FastAPI backend, a Next.js frontend, PostgreSQL, Redis, Celery worker definitions,
database migrations, tests, Docker Compose configuration, and CI workflows.

## Stack

- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Poetry
- Frontend: Next.js 15, React 18, TypeScript, Tailwind CSS, Axios
- Runtime services: PostgreSQL 16, Redis 7, optional Celery worker and beat
- Quality tools: Ruff, mypy, pytest, ESLint, Prettier, Vitest, pre-commit

## Quick Start

Requirements:

- Docker 20.10+
- Docker Compose v2
- Git

Start the development stack:

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

The backend container runs `alembic upgrade head` before starting FastAPI, so a
fresh database is migrated automatically.

Open:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

Use either `localhost` or `127.0.0.1` for the frontend. The backend CORS config
allows both local origins.

## Project Layout

```text
.
├── backend/              # FastAPI app, models, migrations, tests
├── frontend/             # Next.js app, components, services, tests
├── docs/                 # Architecture, API, database, and design docs
├── .github/workflows/    # CI/CD workflows
├── docker-compose.yml    # Local development stack
├── CHANGELOG.md          # Release notes
├── CONTRIBUTING.md       # Contribution guide
└── README.md             # Project entry point
```

## Development

Backend:

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Docker helpers:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose restart backend
docker compose down
```

Optional workers:

```bash
docker compose --profile workers up -d
```

## Checks

Run the main checks locally:

```bash
pre-commit run --all-files
```

Backend:

```bash
cd backend
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app --ignore-missing-imports
```

Frontend:

```bash
cd frontend
npm run lint
npm run type-check
npm run format:check
npm test
```

## Documentation

- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)
- Architecture docs: [docs/architecture/](docs/architecture/)
- WebSocket API docs: [docs/api/websocket.md](docs/api/websocket.md)
- Database docs: [docs/database.md](docs/database.md)
- Development notes: [docs/development.md](docs/development.md)

## Notes

- `docker compose up -d` starts frontend, backend, PostgreSQL, and Redis.
- Celery services are behind the `workers` profile and are not started by default.
- Do not commit generated coverage artifacts or local virtual environments.
