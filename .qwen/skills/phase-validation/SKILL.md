---
name: phase-validation
description: Systematic methodology for validating that a project phase/spec is fully implemented by cross-referencing every requirement against actual codebase artifacts.
source: auto-skill
extracted_at: '2026-06-09T22:14:12.020Z'
---

## Purpose

When a user asks to validate whether a development phase or feature spec is "fully implemented," use this systematic approach to produce a concrete, evidence-based compliance report — not a vague summary.

## Procedure

### 1. Ingest the specification

- Read the phase/spec document in full.
- Extract **every numbered requirement**, section header, and Definition of Done criterion.
- Build a mental (or explicit) checklist mapping section numbers to what must exist in code.

### 2. Map spec sections to code artifacts

For a typical backend phase, check these layers in order:

| Spec concern | Where to look in code |
|---|---|
| Data model / entity | `models/*.py` — ORM class, fields, relationships, FKs |
| Schemas / contracts | `schemas/*.py` — Pydantic request/response models |
| Repository / data access | `repositories/*.py` — queries, joins, permission checks |
| Business logic | `services/*.py` — orchestration, validation methods |
| API endpoints | `routes/*.py` — HTTP methods, paths, status codes, response models |
| File storage | `integrations/storage/` or `services/*storage*` — save, delete, paths |
| Database migrations | `migrations/versions/` — table creation, columns, constraints |
| Tests | `tests/` — unit, integration, edge cases |
| Admin/other integrations | `routes/admin.py` or similar — detail views, listings |

### 3. Verify each requirement individually

For every requirement in the spec:

- **Navigate** to the relevant file(s).
- **Confirm** the artifact exists and implements the requirement.
- **Mark** as ✅ (complete), ⚠️ (partial/concern), or ❌ (missing).
- **Record the evidence**: file path, function/class name, or code snippet that proves compliance.

### 4. Check the Definition of Done explicitly

Most specs have a "Definition of Done" or acceptance criteria section. Evaluate each criterion independently — don't assume "if the endpoint exists, the DoD is met."

### 5. Check for tests

- Grep the `tests/` directory for keywords related to the feature.
- If no tests exist, flag this as a gap regardless of how complete the implementation looks.

### 6. Separate backend from frontend

- If the spec covers both backend and frontend but the current repo is backend-only, clearly separate the two in the report.
- Don't penalize a backend repo for missing frontend work, but document that the frontend portion belongs elsewhere.

### 7. Produce a structured report

Format the output as:

1. **Summary line** — percentage complete, split by backend/frontend if applicable.
2. **Complete items table** — requirement, status, file evidence.
3. **Incomplete/gap table** — what's missing, why it matters.
4. **DoD evaluation** — criterion-by-criterion pass/fail.
5. **Conclusion + recommendation** — what would bring it to 100%.

## Key principles

- **Evidence over assertion**: Every status claim must point to a file and artifact.
- **Section-by-section**: Don't skip spec sections. Even "obvious" ones (like storage strategy) need verification.
- **Permission checks matter**: A feature isn't complete if it lacks authorization/ownership validation.
- **Tests are part of completeness**: Untested code is incomplete code.
- **Cascade behavior**: Check that related operations (delete item → delete supports) are handled.
