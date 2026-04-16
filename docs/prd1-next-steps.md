# PRD 1 Next Steps

This checklist is based on the work currently merged for PRD 1 plus the repo's local engineering guidance. It should be treated as a working handoff until the source PRD is reopened and confirmed.

## Done

- Auth setup is in place:
  - magic link request + verification
  - JWT access/refresh token flow
  - admin-gated registration
  - frontend login / verify flow
- Project CRUD backend is in place:
  - `Project` model
  - Alembic migration
  - authenticated `/api/projects` endpoints
  - integration coverage for create/list/get/update/delete
- Local PR workflow notes were updated:
  - PR template no longer adds the Claude footer
  - PR titles now require Conventional Commits prefixes

## Next

- [ ] Refactor project endpoint logic into a service layer
  - Create `api/renovaite/services/project.py`
  - Move create/list/get/update/delete business logic out of `api/renovaite/api/projects.py`
  - Keep router responsibilities limited to request/response wiring
- [ ] Add missing project API edge-case coverage
  - `404` for updating a nonexistent project
  - `404` for deleting a nonexistent project
  - `403` for updating another user's project
  - `403` for deleting another user's project
  - request validation failures for malformed project payloads
- [ ] Confirm whether PRD 1 includes frontend project management screens
  - If yes, define the next slice as list/detail/create-edit UX
  - If no, keep PRD 1 backend-only and move to the next PRD milestone

## Open Questions

- Does PRD 1 require frontend project pages now, or is the current backend slice sufficient?
- Should project CRUD stay as one endpoint set, or should planning/status fields be added before frontend work starts?
- Do we need to align model IDs with the engineering note that says UUID PKs, given the current implementation uses integer IDs?

## Recommended Next Branch

- `prd1/refactor-project-service`

## Resume Commands

```bash
git switch main
git pull --ff-only
git switch -c prd1/refactor-project-service

cd api
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest
env UV_CACHE_DIR=/tmp/uv-cache uv run mypy renovaite

cd ../web
pnpm test
```

## Notes

- Use `UV_CACHE_DIR=/tmp/uv-cache` when `uv` cache permissions are an issue.
- Keep PR titles in Conventional Commits format:
  - `feat: ...`
  - `fix: ...`
  - `chore: ...`
  - `docs: ...`
  - `refactor: ...`
  - `style: ...`
  - `test: ...`
  - `perf: ...`
