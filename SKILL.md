---
name: backend-fastapi-platform
description: build and evolve the backend for a greenfield fastapi project with a quality-first architecture. use when designing modules, endpoints, schemas, services, repositories, auth flows, file upload, ai integration, evaluation rules, admin dashboards, migrations, and delivery plans for a fastapi + postgresql system. prioritize proven libraries and framework capabilities before custom infrastructure, especially pydantic, sqlalchemy, alembic, fastapi dependency injection, python-multipart, passlib or pwdlib, jose-compatible jwt tooling, and httpx for external integrations.
---

# Backend FastAPI Platform

Build production-ready FastAPI code with a maintainable layered architecture for this project.

## Default stack

Use these defaults unless the user explicitly overrides them:

- FastAPI
- Python 3.12+
- Pydantic v2 for schemas and settings
- SQLAlchemy 2.x ORM
- Alembic for migrations
- PostgreSQL
- `python-multipart` for file uploads
- `pwdlib` or `passlib` for password hashing
- `python-jose` or equivalent JWT library for tokens
- `httpx` for external HTTP calls
- `pytest` for tests
- `uvicorn` for local dev

## Core rule: prefer framework and library features before custom logic

Use FastAPI and ecosystem primitives first.

Follow this priority order:

1. FastAPI built-in feature or well-supported ecosystem library
2. Thin project wrapper around that capability
3. Custom logic only for domain-specific behavior

Apply this rule strictly for:

- request validation -> Pydantic models
- dependency management -> FastAPI dependencies
- password hashing -> passlib or pwdlib
- auth tokens -> jose-compatible JWT library
- database access -> SQLAlchemy session pattern
- migrations -> Alembic
- multipart upload -> python-multipart
- external API integration -> httpx client
- configuration -> pydantic settings

Do not create:

- homemade validation layers duplicating Pydantic
- raw SQL scattered across endpoints without reason
- ad hoc authentication code inside route handlers
- giant controller files with business logic and persistence mixed together
- custom migration systems

## Project architecture

Use this layered structure:

```text
app/
  api/
    deps/
    routes/
  core/
    config.py
    security.py
    exceptions.py
  db/
    base.py
    session.py
    models/
    migrations/
  modules/
    auth/
      schemas/
      service.py
      repository.py
    users/
    applications/
    cv_processing/
    evaluation/
    results/
    admin/
    calls/
  integrations/
    gemini/
    storage/
  tests/
```

Rules:

- Routes handle transport only
- Services own business rules and orchestration
- Repositories own database queries and persistence details
- Pydantic schemas define input and output contracts
- External providers live under `integrations/`
- Keep module boundaries explicit

## Backend delivery workflow

1. Identify the requested module: auth, users, postulation, hoja de vida, soportes, results, admin, ai extraction, or rules engine
2. Check `references/project-context.md` for domain scope
3. Check `references/backend-architecture.md` for placement and conventions
4. Check `references/backend-feature-playbook.md` for the build checklist
5. Create schema contracts first, then service boundaries, then repository queries, then routes
6. Add tests for critical rules before calling the module complete

## Required engineering standards

Every backend deliverable must include:

- clear module placement
- request and response schemas
- service layer with explicit responsibilities
- repository or persistence layer for DB operations
- structured error handling
- auth and permission considerations when relevant
- migration impact note if models change
- test recommendations or actual tests for critical logic

## Required patterns by feature type

### Authentication

For login and protected routes:

- Separate hashing, token generation, and credential validation into `core/security.py` or auth service helpers
- Keep route handlers thin
- Return explicit auth response schemas
- Centralize current-user dependency
- Add role-aware authorization dependencies only when needed

### CV upload and IA extraction

For CV ingestion flows:

- Accept multipart upload with file size and extension validation
- Separate storage/upload from extraction orchestration
- Keep Gemini or external AI interaction in `integrations/gemini/`
- Normalize extracted payloads into internal domain schemas before persistence
- Distinguish upload failure, parse failure, extraction failure, and mapping failure

### Hoja de vida and postulation

For editable extracted profile data:

- Model repeated records explicitly: experience, formation, production, supports
- Use transactional service methods for save-draft or submit-postulation flows
- Keep domain status transitions in service logic, not in routes
- Validate ownership and convocatoria constraints centrally

### Results and admin

For ranking and dashboard flows:

- Prefer filter schemas for query params
- Keep sorting and pagination explicit
- Return compact list schemas plus detail schemas
- Expose computed fields through response models, not route-side dict assembly

### Evaluation rules

For rule configuration and scoring:

- Keep scoring engine as a dedicated service module
- Separate configuration data from execution logic
- Make pure score-calculation functions testable without the web layer
- Persist score snapshots where the domain needs auditability

## API style rules

- Use `/api/v1/...` versioned prefixes unless the user asks otherwise
- Use nouns for resources
- Prefer explicit action endpoints only for true commands such as `/postulations/{id}/submit`
- Keep response models declared on routes
- Return consistent error shapes when possible

## Output format for implementation requests

When the user asks for a module or feature, respond in this order unless they explicitly ask only for code:

1. Brief architecture note
2. File tree to create or edit
3. SQLAlchemy models or migration updates if needed
4. Pydantic schemas
5. repository layer
6. service layer
7. route layer
8. tests or validation notes

## Project-specific priorities

This project currently centers on:

- login
- formato de hoja de vida editable after CV extraction
- muestras de resultados
- solid foundations for convocatoria management, rules engine, and admin dashboard

Bias implementations toward those flows first.

## Quality gates before finishing

Before finalizing any backend deliverable, verify:

- routes are thin
- Pydantic models cover input and output
- transactions are placed intentionally
- repository and service concerns are not mixed
- auth and authorization were considered
- migrations are coherent with the current data model
- domain errors are surfaced clearly
- code supports future AI extraction and scoring modules without rework

## References

- Use `references/project-context.md` for domain scope and entities
- Use `references/backend-architecture.md` for code organization and module rules
- Use `references/backend-feature-playbook.md` for implementation checklists and templates
