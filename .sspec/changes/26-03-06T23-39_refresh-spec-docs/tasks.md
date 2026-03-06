---
change: "refresh-spec-docs"
updated: "2026-03-07T00:53"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Repair Existing Docs ⏳
### Phase 1: Repair Existing Docs ✅
- [x] Update `.sspec/project.md` — refresh stack, key paths, conventions, and spec-doc pointers against the live repo
- [x] Update `.sspec/spec-docs/README.md` — sync index coverage and navigation with the actual spec-doc set
- [x] Update `.sspec/spec-docs/skill-installation.md` — correct workspace targets, link behavior, and migration notes
- [x] Update `.sspec/spec-docs/builtin-tools.md` — document `patch`, `pack-zip`, `view-tree`, and `mdtoc`
- [x] Update `.sspec/spec-docs/testing-standards.md` — remove dead module references and align coverage guidance with current tests
**Verification**: Every changed statement is cross-checked against the current code paths it documents.

### Phase 2: Add Missing Contract Docs ✅
- [x] Create `.sspec/spec-docs/change-lifecycle.md` — document change structure, status parsing, archive flow, and reference rewrites
- [x] Create `.sspec/spec-docs/interaction-records.md` — document request/ask schemas, linking, completion, and archive semantics
- [x] Create `.sspec/spec-docs/cmd-registry.md` — document `.sspec/commands/registry.yaml` and script strategies
- [x] Create `.sspec/spec-docs/agents-sync.md` — document root `AGENTS.md` managed block behavior
**Verification**: New docs follow `write-spec-doc` requirements: frontmatter complete, scope concrete, content tied to real code paths.

### Phase 3: Reindex and Verify the Doc Set ✅
- [x] Cross-link `.sspec/project.md` and `.sspec/spec-docs/README.md` to all new and updated docs
- [x] Run a doc consistency pass over `.sspec/spec-docs/` and fix any stale paths or missing cross-references
- [x] Update `.sspec/changes/26-03-06T23-39_refresh-spec-docs/handover.md` and progress to match the delivered documentation state
**Verification**: The spec-doc set is internally navigable, indexed, and free of known stale references from this audit.

### Feedback Tasks
- [ ] (none yet)

<!-- @RULE: Organize by phases. Each task <2h, independently testable.
Phase emoji: ⏳ pending | 🚧 in progress | ✅ done

### Phase 1: <name> ⏳
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>

### Feedback Tasks
Use this section for tasks added during review/feedback loop.
-->

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- 2026-03-07T00:53 - User accepted the doc refresh batch and requested finalization + commit
- 2026-03-07T00:15 - Completed doc refresh implementation; status moves to REVIEW pending user feedback
- 2026-03-06T23:49 - User approved current scope; change transitions from PLANNING to DOING
- 2026-03-06T23:40 - Created change and drafted design/tasks for spec-doc refresh transaction
