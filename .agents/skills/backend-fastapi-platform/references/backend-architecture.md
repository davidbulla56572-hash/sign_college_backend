# Backend Architecture

## Guiding principles
- Thin routes, rich services
- Explicit schemas at the edges
- Transactions around use cases, not random helper calls
- Integrations isolated from domain logic
- Test pure business rules independently from the API layer

## Core folders

### api/routes
Expose HTTP endpoints and translate request to service calls.

### api/deps
Place reusable dependencies here:
- db session provider
- current user
- admin authorization
- pagination or filter helpers if shared

### core
Place cross-cutting backend concerns here:
- settings
- security helpers
- exception classes
- logging setup

### db/models
Keep SQLAlchemy models here, one file per aggregate or a small grouped set.

### modules/<feature>
Each module should usually contain:
- schemas/
- repository.py
- service.py
- optional selectors.py or policies.py when the domain justifies it

### integrations
Keep external dependencies isolated here:
- gemini client
- storage provider
- email or notification provider later if needed

## Data conventions
- Use integer primary keys unless the user asks otherwise
- Keep created_at and updated_at timestamps on main aggregates when helpful
- Prefer enum-backed constrained states for postulation and role values
- Reflect DB constraints through service logic too, not only schema definitions

## Testing direction
When asked for tests, prioritize:
- auth service tests
- score engine tests
- CV mapping tests
- route smoke tests for critical modules
