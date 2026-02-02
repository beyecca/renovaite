# RenoBrain

Monorepo: API (Django + Ninja) and Web (React + Vite).

## Development

### API (`api/`)

- Python 3.12, [uv](https://docs.astral.sh/uv/)
- From `api/`: `uv sync --dev`, then `uv run python manage.py runserver` (or `uv run uvicorn ...`)

### Web (`web/`)

- Node 20+, pnpm
- From `web/`: `pnpm install`, then `pnpm dev`

## Linting and type checking

- **API**: Ruff (format + lint), Mypy. From `api/`: `uv run ruff format . && uv run ruff check .`, `uv run mypy app`
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

1. **API**: Ruff (format check + lint), Mypy, compileall, `manage.py check`
2. **Web**: ESLint, TypeScript typecheck, Vite build
3. **Docker**: Build API image (after API job passes)

Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml).
