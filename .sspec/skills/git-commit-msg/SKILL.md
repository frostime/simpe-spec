---
name: git-commit-msg
description: Conventional Commits + emoji prefix used in this repository.
metadata:
  author: sspec
  version: 1.0.0
---

# Git Commit Message Convention

## Format

```text
<emoji> <type>(<scope>): <short msg>

<optional detailed msg>
```

- `<scope>` is optional.
- Keep `<short msg>` <= 72 chars when possible.
- Use a blank line before the detailed message.

### Examples

```text
🐛 fix(meta): normalize skill_install_strategies keys
```

```text
✨ feat(cli): add project update dry-run summary

- show skill migrations and orphan removals
- keep output stable on Windows terminals
```

```text
📝 docs: document commit message convention
```

## Types (Emoji Mapping)

Core types follow Conventional Commits (feat, fix, refactor, ...). Extra types
exist for common repo workflows (move, delete, wip, ...).

```text
✨ feat:     new feature
🐛 fix:      bug fix
♻️ refactor: refactor without behavior change
📝 docs:     documentation only
🎨 style:    formatting / structure (no logic change)
⚡️ perf:     performance improvement
✅ test:     tests only
📦 chore:    tooling, deps, maintenance
👷 ci:       CI/CD changes
🚧 wip:      work in progress (avoid on main)
🚚 move:     move/rename files
🔥 delete:   remove code/files
⏪ revert:   revert a previous commit
🎉 init:     project init / first commit
🔀 merge:    merge branches
```

Optional (usually hidden unless needed):

```text
🔧 config:   config file changes
🔖 tag:      release/tagging
```

## Scope

Use `<scope>` to name the area being changed. Keep it short and consistent.

Common scopes:

```text
meta, skills, templates, cli, services, installer, docs, tests
```

## Detailed Message

Use the detailed message when the "why" is not obvious from the subject.

- Prefer 1-3 bullets.
- Explain intent, constraints, and user impact.
- Avoid file-by-file change logs.

## Breaking Changes (Optional)

If you intentionally break behavior/API, use Conventional Commits breaking
change markers:

```text
✨ feat(api)!: change meta schema markers

BREAKING CHANGE: .meta.json now requires meta_schema and sspec_schema.
```
