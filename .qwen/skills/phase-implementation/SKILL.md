---
name: phase-implementation
description: Systematic methodology for implementing a new development phase/spec in a FastAPI backend, from spec ingestion to verified delivery.
source: auto-skill
extracted_at: '2026-06-09T22:23:09.549Z'
---

## Purpose

When given a phase specification document (e.g., `fase_13_validacion_admin_items_trazabilidad.md`) to implement in a FastAPI backend, use this systematic approach to ensure complete, coherent delivery.

## Procedure

### 1. Ingest the spec

- Read the phase document in full.
- Extract the **expected endpoints** (usually in a "Endpoints minimos esperados" section).
- Extract the **expected response contracts** (JSON examples or schema descriptions).
- Extract **validation rules** (permissions, file types, ownership checks).
- Extract **DoD criteria** (what "done" means for this phase).

### 2. Audit existing code for gaps

Before creating anything new:

- Check if any of the expected endpoints already exist (even partially).
- Check if models already have the required fields.
- Check if schemas partially exist.
- Check existing services for reusable methods.
- Map what's **missing** vs. what's **present**.

### 3. Implement in layer order (bottom-up)

Follow this order to avoid circular dependencies and rework:

| Step | Layer | What to do |
|---|---|---|
| 1 | Schemas | Create/extend Pydantic models for requests and responses. Put them in the relevant module's `schemas/` directory. |
| 2 | Service | Create the service class with all business logic. Keep it independent of FastAPI — use `Session`, not `Depends`. |
| 3 | Repository | Only if existing repositories don't cover the queries. Add methods for data access with permission checks. |
| 4 | Routes | Create/update route files. Wire up `Depends()` for DB session, auth, and service. Define response_model. |
| 5 | Router registration | Add the route module to `app/api/router.py` if it's a new file. |

### 4. Schema design rules

- **Response schemas**: Mirror the spec's JSON contract exactly. Include all fields mentioned.
- **Request schemas**: Use Pydantic validation (`Field`, constraints) for inputs.
- **Reuse existing types**: If `TipoItemHojaVida` or `PostulacionEstado` already exist as enums, use them — don't recreate.
- **Nesting**: If the spec says "items with soportes nested," create `AdminItemDetalle` with `soportes: list[AdminSoporteItemSimple]`, not a flat list.
- **Optional fields**: Use `str | None = None` for nullable/optional fields per the spec.

### 5. Service design rules

- **No FastAPI imports** in services — keep them framework-agnostic.
- **Constructor injection**: Accept `Session` or repositories via `__init__`.
- **Permission checks in service or repository**, not in routes.
- **Raise `NotFoundError`** when resources don't exist — the exception handler converts it to HTTP 404.
- **Return schemas**, not dicts. This ensures serialization consistency.
- **Group related operations** in one service class (e.g., `AdminPostulacionReviewService` handles detalle, validation, observaciones, trace).

### 6. Route design rules

- **Thin routes**: The route function should be 5-10 lines — get dependencies, call service, return result.
- **`Depends()` pattern**:
  ```python
  def _get_service(db: Session = Depends(get_db)) -> SomeService:
      return SomeService(db)
  ```
- **Auth**: Use `require_admin_role` or `get_current_active_user` as appropriate.
- **`response_model`**: Always set it — this validates and serializes the response.
- **Status codes**: Use `status_code=201` for creation, `204` for deletion, default 200 otherwise.
- **Keep existing endpoints**: Don't replace old endpoints; add new ones alongside them.

### 7. Verify before declaring done

Run these checks:

```bash
# App loads without errors
python -c "from app.main import app; print('OK')"

# All routes are registered
python -c "from app.main import app; print([r.path for r in app.routes])"

# Schemas serialize correctly
python -c "from app.modules.X.schemas import Y; print(Y(...).model_dump())"

# OpenAPI includes new endpoints
python -c "from app.main import app; paths = app.openapi()['paths']; print([p for p in paths if '/new/' in p])"
```

### 7b. Spec document location

Phase specification documents may live in the **parent directory** of the project repo, not inside it:
- Pattern: `../fase_N_<description>.md` (e.g., `../fase_13_validacion_admin_items_trazabilidad.md`)
- If the user mentions a phase number but the file isn't in the project, check `../` with `glob` or `read_file`.

### 8. Update documentation

- Add new endpoints to `README.md` endpoint table.
- Tag with phase number if applicable (e.g., "(Fase 13)").

### 8b. Refactoring existing services (when a phase strengthens existing logic)

When a phase requires **robustecimiento** or refinement of an existing service (not creating from scratch):

- **Audit first**: Read the existing service completely. Identify gaps against the spec's requirements.
- **Refactor in-place**: Update the existing service class rather than creating a parallel one. Preserve the public API for backward compatibility.
- **Handle edge cases explicitly**: If the spec says "items without rules," don't raise an error — assign 0 pts and report as a warning. Let the spec dictate whether something is an error or a handled edge case.
- **Make operations idempotent/re-executable**: If the spec mentions recalculation, design the evaluation so it can run multiple times with consistent results. Reset state before re-executing if needed.
- **Schema extension for backward compat**: Add new fields with defaults (`items_sin_regla: int = 0`, `advertencias: list[str] = Field(default_factory=list)`) so existing code that doesn't use them still works.
- **Delegate, don't duplicate**: If a new service (e.g., `EvaluationService`) has better logic for an operation, have the old service (e.g., `AdminPostulacionReviewService`) delegate to it rather than maintaining two implementations.

### 9. Cross-repo coordination (when frontend is separate)

If the phase spec includes frontend requirements but lives in a backend-only repo:

- **Implement the backend fully first** — types, schemas, service, routes, tests.
- **Document what the frontend needs**: list the endpoints, contracts, and auth requirements.
- **Locate the frontend repo** (usually a sibling directory like `../<project>_frontend`).
- **Follow the frontend phase implementation skill** (`frontend-phase-implementation`) for the UI layer.
- **Treat them as one delivery**: both backend and frontend must be complete for the phase to be "done" per the spec's DoD.

## Key principles

- **Schemas first**: You can't build routes or services without knowing the contracts.
- **Bottom-up**: Models → Schemas → Services → Routes → Router. Never the reverse.
- **Preserve backward compatibility**: Add new endpoints alongside existing ones. Don't break old clients.
- **One service per domain concern**: Don't scatter related logic across multiple services.
- **Permission checks are mandatory**: Every admin endpoint must verify admin role. Every user endpoint must verify ownership.
- **Verify at every step**: Don't wait until the end to check if the app loads.
- **Phase specs cover both layers**: Backend completeness ≠ phase completeness. If the spec has frontend requirements, the phase isn't done until both are implemented.
