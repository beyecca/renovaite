# RenovAIte

Monorepo: API (Django + Ninja) and Web (React + Vite).

## Structure

```
renovaite/
├── api/                        # Django + Ninja API
│   ├── renovaite/
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings
│   │   │   ├── dev.py          # Local development
│   │   │   └── prod.py         # Production (env-var-driven)
│   │   ├── api/                # Endpoints
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── ai/
│   └── manage.py
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
- From `api/`: `uv sync --dev`, then `uv run python manage.py runserver`

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

1. **API**: Ruff (format check + lint), Mypy, compileall, `manage.py check`, pytest
2. **Web**: ESLint, TypeScript typecheck, Vite build
3. **Docker**: Build API image (after API job passes)

Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Releases and changelog

- **PR titles** must follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat: add login`, `fix: api timeout`). The PR title check enforces this.
- **Changelog** is maintained by [Release Please](https://github.com/googleapis/release-please). On every push to `main`, it opens or updates a **Release PR** that updates [CHANGELOG.md](CHANGELOG.md) from conventional commits.
- **To release**: Merge the Release PR. That updates `CHANGELOG.md` and creates the Git tag and GitHub Release.
