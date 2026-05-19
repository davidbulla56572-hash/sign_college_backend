# Backend Feature Playbook

## Default build checklist
1. Clarify module responsibility
2. Define request and response schemas
3. Define persistence needs and migration impact
4. Create repository methods
5. Create service orchestration
6. Add route handlers and dependencies
7. Add error handling paths
8. Add or propose tests
9. Note integration points with frontend

## Template: auth module
- login request schema
- auth response schema
- auth repository for user lookup
- auth service for credential verification and token generation
- auth route
- current user dependency

## Template: postulation module
- create or update draft schema
- submit command schema if needed
- repository for ownership-safe reads and writes
- service for save, submit, and status changes
- route set for read, save draft, submit, status detail

## Template: CV processing module
- upload schema or file contract
- storage abstraction
- extraction integration client
- extraction mapper
- service that orchestrates upload and extraction
- route that returns normalized editable payload

## Template: results module
- filters schema
- list response schema
- detail response schema
- repository queries for ranking and detail
- service for visibility rules
- admin and aspirant routes or role-aware branching
