# Renovaite — Claude Code Context

Renovaite is a Django + React application that helps homeowners plan renovation projects by generating structured plans with AI. The backend uses Django 5 + Django Ninja + PostgreSQL. The frontend uses React + TypeScript + Vite + Tailwind + shadcn/ui.

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
  api/                        # Django backend
    renovaite/
      models/                 # Django models
      api/                    # Django Ninja routers + endpoints
      services/               # Business logic (no direct DB calls in views)
      schemas/                # Pydantic schemas (in/out)
      ai/                     # AI-related services (future)
      settings/               # Django settings
      urls.py
      manage.py
    tests/                    # Integration + unit tests
    .env.example              # Required env vars — keep up to date
  web/                        # React frontend
  infra/                      # Infrastructure config
  docker-compose.yml
```

---

## Key standards (full detail in engineering standards skill)

- **Auth:** JWT via `django-ninja-jwt`. All endpoints require auth. Apply `JWTAuth()` at router level.
- **Permissions:** Every query must be scoped to `request.user`. Never return another user's data.
- **Models:** UUID PKs, `created_at`, `updated_at`, `is_deleted` on all models. Never hard delete.
- **Errors:** Always return `{ "error": str, "code": str }`. Never leak internals.
- **Tests:** Unit tests for all service logic. Integration tests for all endpoints (happy path, 401, 403, 404).
- **Migrations:** Always use Django migrations. Never modify schema manually.
- **Secrets:** Never hardcode. All secrets via environment variables.

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

Business logic lives in `api/renovaite/services/` — not in views or routers.

```python
# ✅ correct
@router.post("/projects")
def create_project(request, payload: ProjectIn):
    project = ProjectService.create(user=request.user, data=payload)
    return 201, project

# ❌ wrong — logic in the view
@router.post("/projects")
def create_project(request, payload: ProjectIn):
    project = Project(user=request.user, **payload.dict())
    project.save()
    return 201, project
```

---

## Running locally

```bash
cd api
cp .env.example .env        # fill in values
uv run manage.py migrate
uv run manage.py runserver
```

Tests:
```bash
cd api
uv run pytest
```
