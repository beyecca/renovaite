# Renovaite — Claude Code Context

Renovaite is a FastAPI + React application that helps homeowners plan renovation projects by generating structured plans with AI. The backend uses FastAPI + SQLModel + Alembic + PostgreSQL. The frontend uses React + TypeScript + Vite + Tailwind + shadcn/ui.

---

## Before starting any task

1. **Read the engineering standards skill** — all implementation must follow these rules:
   `renovaite-engineering-standards/SKILL.md`

2. **Read the relevant PRD from Notion** — the PRD is the source of truth for what to build.
   Ask the user to provide the Notion workspace URL, PRDs database URL, and the specific PRD URL before proceeding.

3. **Confirm the task and branch name before writing any code.** Branch convention:
   `prd{N}/feat-short-desc` (e.g. `prd1/feat-project-model`, `prd1.5/feat-plan-builder`)

---

## Repo structure

```
renovaite/
  api/                        # FastAPI backend
    renovaite/
      models/                 # SQLModel table classes
      api/                    # FastAPI routers + endpoints
      services/               # Business logic (no direct DB calls in routers)
      schemas/                # Pydantic schemas (in/out)
      ai/                     # AI-related services (future)
      settings/               # pydantic-settings config
      db.py                   # SQLAlchemy engine + get_session dependency
      main.py                 # FastAPI app factory + router mounts
    alembic/                  # Alembic migrations
    tests/                    # Integration + unit tests
    .env.example              # Required env vars — keep up to date
  web/                        # React frontend
  infra/                      # Infrastructure config
  docker-compose.yml
```

---

## Key standards (full detail in engineering standards skill)

- **Auth:** JWT via `PyJWT`. All endpoints require auth. Use a `current_user` FastAPI dependency on protected routers.
- **Permissions:** Every query must be scoped to the authenticated user. Never return another user's data.
- **Models:** UUID PKs, `created_at`, `updated_at`, `is_deleted` on all models. Never hard delete.
- **Errors:** Always return `{ "error": str, "code": str }`. Never leak internals.
- **Tests:** Unit tests for all service logic. Integration tests for all endpoints (happy path, 401, 403, 404).
- **Migrations:** Always use Alembic migrations (`alembic revision --autogenerate`). Never modify schema manually.
- **Secrets:** Never hardcode. All secrets via environment variables + pydantic-settings.

---

## Commit convention

Include the Notion task or PRD reference in every commit message:

```
feat: implement Project model and migrations [prd1/feat-project-model]
fix: enforce ownership check on GET /projects [prd1/feat-auth]
```

---

## Notion task tracking

When completing a task:
1. Update the task status in the Notion Tasks DB to `In Review` or `Done`
2. Add the branch name to the `Branch / PR` field on the task

Ask the user to provide the Notion Tasks DB URL if needed.

---

## Services pattern

Business logic lives in `api/renovaite/services/` — not in routers.

```python
# ✅ correct
@router.post("/projects", status_code=201)
def create_project(payload: ProjectIn, db: Session = Depends(get_session), user: User = Depends(current_user)):
    project = ProjectService.create(user=user, data=payload, db=db)
    return project

# ❌ wrong — logic in the router
@router.post("/projects", status_code=201)
def create_project(payload: ProjectIn, db: Session = Depends(get_session)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    return project
```

---

## Running locally

```bash
cd api
cp .env.example .env                          # fill in values
uv run alembic upgrade head                   # run migrations
uv run uvicorn renovaite.main:app --reload    # start dev server
```

Tests:
```bash
cd api
uv run pytest
```
