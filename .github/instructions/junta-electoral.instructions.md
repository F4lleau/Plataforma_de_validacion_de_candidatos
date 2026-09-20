---
description: "Use when working on the Junta Electoral backend, frontend, API endpoints, schema changes, migrations, documentation, or project setup. Covers repo-specific workflow, architecture awareness, and required documentation updates."
applyTo: ["backend/**", "frontend/**", "AGENTE.md", "**/README.md"]
---

# Junta Electoral Development Guidelines

## Before making changes

- Read the project documentation first: [backend/README.md](../../backend/README.md) and [frontend/README.md](../../frontend/README.md).
- Check the files directly related to the feature, module, or bug being changed before editing.
- Keep the stack context in mind: FastAPI + SQLAlchemy + Alembic for the backend and React + TypeScript + Vite + Tailwind for the frontend.
- Prefer the smallest change that solves the problem and stays aligned with the existing architecture.

## Required workflow

- Review the relevant backend/frontend structure and naming patterns before creating or modifying code.
- For data model or database changes, inspect the current migration patterns and ensure the change is safe and reversible.
- When changing APIs, environment variables, dependencies, migrations, user flows, or business rules, update the relevant documentation.
- Preserve separation of concerns between backend logic, frontend UI, and shared configuration.
- Keep comments and documentation clear, practical, and useful for future contributors.

## Documentation rules

- Update the relevant README or project docs whenever a feature, endpoint, workflow, dependency, or setup step changes.
- Prefer concise project documentation over duplicated long explanations.
- Document environment variables, migrations, integration dependencies, and operational procedures when they affect local development or deployment.
- If a fix changes behavior, make sure the docs reflect the new flow or requirement.

## Validation expectations

- Validate the affected behavior with the most relevant command, test, or smoke check available.
- Do not claim a fix or completion without evidence from the command output or relevant validation step.
- If a change touches the backend database layer, verify the migration and runtime assumptions are still consistent.

## Repository-specific conventions

- Keep backend files under `backend/app/` organized by responsibility such as models, repositories, services, schemas, and API routes.
- Keep frontend code organized by modules and features instead of scattering logic across unrelated files.
- Match the repository’s conventions for naming, imports, and architecture rather than introducing ad hoc patterns.

## Summary

The goal is to keep the project coherent, maintainable, and easy for new developers to understand while preserving the established FastAPI and React architecture.
