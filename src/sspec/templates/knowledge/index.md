# Project Context

**Read this file before starting any work on this project.**

---

## Overview

**Name**: [project-name]
**Description**: [One-line description of what this project does]
**Repository**: [URL if applicable]

### Tech Stack

<!-- Example:
- **Language**: TypeScript 5.2+
- **Framework**: Express 4.18, Socket.io 4.6
- **Key Dependencies**: Prisma (ORM), Zod (validation), Winston (logging)
- **Build Tool**: esbuild
- **Test Framework**: Jest + Supertest
- **Database**: PostgreSQL 15
-->

## Project usage

<!-- How to run, debug, build the project -->

---

## Knowledge Files

<!--
Map of specialized knowledge documents.
Create these files as the project grows.
-->

| File | Content |
|------|---------|
| `index.md` | This file — project overview |
<!-- Examples
|`architecture.md` | System design, component relationships |
| `api-design.md` | API conventions, error codes, versioning |
| `security.md` | Authentication flow, authorization rules |
| `deployment.md` | CI/CD pipeline, environment setup |
-->

<!-- Start with just index.md, add others as needed -->

---

## Conventions

<!--
AI MUST follow these rules. Be SPECIFIC, not vague.
-->

### Code Style

<!--
❌ Bad (too vague):
- Use consistent naming
- Follow best practices

✅ Good (specific and enforceable):
-->

<!-- Example:

**Naming**:
- Files: `kebab-case.ts` (e.g., `user-service.ts`)
- Folders: `kebab-case` (e.g., `auth-middleware/`)
- Variables/functions: `camelCase` (e.g., `getUserById`)
- Classes/types: `PascalCase` (e.g., `UserService`, `AuthToken`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)

**Project-Specific Rules**:
- All API routes in `src/routes/` directory
- Business logic in `src/services/`, NOT in route handlers
- Database queries ONLY through Prisma, no raw SQL
- All inputs validated with Zod schemas before processing

**Error Handling**:
- Use custom error classes: `AppError`, `ValidationError`, `NotFoundError`
- Never throw generic `Error` — use specific error types
- API errors return JSON: `{ error: string, code: string, details?: any }`
-->


### Testing Requirements

<!-- Adjust based on your project -->

---

## Constraints

<!--
Technical, business, or regulatory limits.
Be specific about WHY and WHAT the limit is.
-->

<!--
Examples:

**Technical**:
- Must support Node.js 18+ (no 20+ features like native test runner)
- Cannot use child_process.exec() — security policy, use execFile() instead
- All external API calls must timeout within 10 seconds

**Business**:
- Free tier limited to 100 requests/hour per user
- File uploads max 10MB (S3 transfer costs)
- Must support IE11 (client requirement until Q3 2025)

**Regulatory**:
- GDPR: All user data deletions must complete within 30 days
- PCI-DSS: No credit card data stored in database (Stripe only)
- HIPAA: All PHI must be encrypted at rest (using AWS KMS)
-->

-

---

## Project Structure

<!--
High-level directory organization and what goes where.
Help AI know where to put new files.
-->

<!-- Examples:
``​`
src/
├── routes/       # Express route handlers (thin, delegate to services)
├── services/     # Business logic (fat, testable)
├── middleware/   # Express middleware (auth, logging, etc)
├── models/       # Prisma schema and types
├── utils/        # Shared utilities (date helpers, validators)
└── config/       # Configuration (env loading, feature flags)
``​`
-->

---

## External References

<!--
Links to docs, APIs, design specs, related repos.
Include internal wikis, Notion pages, Figma designs, etc.
-->

---

<!--
KNOWLEDGE BASE PHILOSOPHY:

This file should answer: "What does a new developer need to know to contribute safely?"

Focus on:
- Non-obvious constraints (not "write tests" but "tests must cover X")
- Project-specific gotchas (not general best practices)
- Concrete examples (not abstract principles)

Update when:
- You discover a new gotcha or constraint
- A convention changes
- A common question gets asked repeatedly

Keep it CONCISE. If it grows beyond ~200 lines, split into multiple knowledge/ files.
-->
