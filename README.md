# RenovAIte

Monorepo: API (FastAPI + SQLModel) and Web (React + Vite).

## Structure

```
renovaite/
├── api/                        # FastAPI + SQLModel API
│   ├── renovaite/
│   │   ├── settings/
│   │   │   ├── base.py         # pydantic-settings BaseSettings
│   │   │   ├── dev.py          # Local development overrides
│   │   │   └── prod.py         # Production (env-var-driven)
│   │   ├── api/                # Endpoints (FastAPI routers)
│   │   ├── models/             # SQLModel table classes
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic
│   │   ├── db.py               # Engine + get_session dependency
│   │   ├── main.py             # App factory + router mounts
│   │   └── ai/
│   └── alembic/                # Database migrations
├── web/                        # React + TypeScript + Vite
│   └── src/
│       ├── routes/             # Page-level components
│       ├── components/         # Shared UI components
│       ├── features/           # Feature modules
│       └── lib/                # Utilities
├── infra/                      # Terraform (AWS)
└── docker-compose.yml
```

## Development

### API (`api/`)

- Python 3.12, [uv](https://docs.astral.sh/uv/)
- From `api/`: `uv sync --dev`, then `uv run alembic upgrade head` and `uv run uvicorn renovaite.main:app --reload`

### Web (`web/`)

- Node 20+, pnpm
- From `web/`: `pnpm install`, then `pnpm dev`

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

### Docker (local container)

Run the API as a container from the repo root:

```bash
docker compose up
```

API available at `http://localhost:8000`.

## Linting and type checking

- **API**: Ruff (format + lint), Mypy. From `api/`: `uv run ruff format . && uv run ruff check .`, `uv run mypy renovaite`
- **Web**: ESLint, TypeScript. From `web/`: `pnpm run lint`, `pnpm run format`, `pnpm run typecheck`

## Pre-commit

Install [pre-commit](https://pre-commit.com/) and run once from the repo root:

```bash
pre-commit install
```

Hooks run on commit: Ruff + Mypy (API), ESLint + tsc (Web). Run manually:

```bash
pre-commit run --all-files
```

## CI (GitHub Actions)

On push/PR to `main`, the workflow runs:

1. **API**: Ruff (format check + lint), Mypy, pytest
2. **Web**: ESLint, TypeScript typecheck, Vite build
3. **Docker**: Build API image (after API job passes)

Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Releases and changelog

- **PR titles** must follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat: add login`, `fix: api timeout`). The PR title check enforces this.
- **Changelog** is maintained by [Release Please](https://github.com/googleapis/release-please). On every push to `main`, it opens or updates a **Release PR** that updates [CHANGELOG.md](CHANGELOG.md) from conventional commits.
- **To release**: Merge the Release PR. That updates `CHANGELOG.md` and creates the Git tag and GitHub Release.
