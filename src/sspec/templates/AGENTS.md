<!-- SSPEC:START -->
# sspec Router

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## Project Context

If `.sspec/project.md` exists, read it before project-specific work.
Use its Key Paths, Conventions, and Spec-Docs Index for orientation.
Read spec-docs only when the current task matches their index entry.

## Full Rule Trigger

Read `.sspec/SSPEC.rule.md` when:
- user mentions sspec, spec, change, request, spec-doc, align, or argue;
- task references `.sspec/requests/*`, `.sspec/changes/*`, or `.sspec/spec-docs/*`;
- user asks to create/update project context, request, change, spec-doc, memory, or workflow state;
- user asks to clarify/design/plan/implement/review using sspec;
- change is non-micro: broad, architectural, API/schema/data/security/privacy/UX affecting, or hard to predict safely.

Micro/local/reversible edits may be done directly.

## Skills

After reading `.sspec/SSPEC.rule.md`, load matching `.sspec/skills/<name>/SKILL.md` before that phase/task.
If a SKILL references relative files, read them relative to that SKILL directory.

## Output Safety

When showing content that contains ` ``` `, outer fence MUST use more backticks (e.g. `````). Always outer > inner.
<!-- SSPEC:END -->
