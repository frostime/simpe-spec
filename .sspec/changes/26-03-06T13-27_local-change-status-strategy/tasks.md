---
change: "local-change-status-strategy"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks
### Phase 1: Research current status/design space ✅
- [x] Inspect current `project status`, `change find`, and commented `change status` flow in `src/sspec/commands/change.py`
- [x] Compare openspec-style status/schema ideas against sspec's local change philosophy
- [x] Write research notes in `reference/status-research.md`
**Verification**: Research can explain why global schema control is a poor fit for sspec.

### Phase 2: Design recommended direction ✅
- [x] Define recommended product boundary: local change truth, CLI as read-only projection
- [x] Define minimal summary fields and bounded extraction strategy in `spec.md`
- [x] Define staged roadmap: human-readable first, JSON later only if justified
**Verification**: `spec.md` clearly answers whether/why sspec should have a dedicated status command.

### Phase 3: User alignment gate ✅
- [x] Ask user whether the proposed direction is feasible before any implementation change
- [x] Incorporate user feedback: source links in status output + only light AGENTS/SKILL guidance
**Verification**: User explicitly accepts / redirects the design.

### Phase 4: Implement local status summary ✅
- [x] Add bounded status summary parsing helpers in `src/sspec/services/change_service.py`
- [x] Restore/add `sspec change status <name>` in `src/sspec/commands/change.py`
**Verification**: `uv run sspec change status local-change-status-strategy` shows status, source links, latest next action, and degrades gracefully.

### Phase 5: Polish guidance and validate ✅
- [x] Add a short quick-dashboard hint in `src/sspec/templates/AGENTS.md`
- [x] Reinstall, lint, format, and smoke-test the CLI in `tmp/`
**Verification**: `uv pip install -e .`, `uv run ruff check src/`, `uv run ruff format src/`, and sandbox CLI checks all pass.

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
| Phase 4 | 100% | ✅ |
| Phase 5 | 100% | ✅ |

**Recent**:
- Wrote research note comparing local summary vs global schema paths
- Drafted design recommending `change status` as a local dashboard, not an orchestrator API
- Incorporated user feedback about source-path links and minimal protocol hints
- Added bounded status summary extraction and restored `sspec change status <name>`
- Reinstalled, linted, formatted, and smoke-tested single/root status output in `tmp/test_change_status_dashboard`
