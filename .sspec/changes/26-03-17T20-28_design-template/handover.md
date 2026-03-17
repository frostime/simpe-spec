# Handover: design-template

**Updated**: 2026-03-17T23:58

---

## Background

Replace the fixed sub-section template (Interface Design / Data Flow / Key Logic) in sspec-design SKILL Step 3A with a "predictability dimensions" menu. Each dimension is a howto card that agents load on demand. Also adds `type` field to howto system for classification and filtering.

## Git Baseline (Immutable)

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `feat/better-design`
- HEAD: `d2d496efc7e92ddcf52c43d68eca3b091d9f7200`
- Worktree: `dirty`
- Status Snapshot: raw `git status --short --branch` output

```text
## feat/better-design
A  .sspec/requests/26-03-17T19-42_design-template.md
```

## Working Memory (Stable)

### Key Files
- `src/sspec/templates/skills/sspec-design/SKILL.md` - Core SKILL rewritten with dimension menu + universal rules
- `src/sspec/templates/change/spec.md` - Template comment updated to reference dimensions
- `src/sspec/services/howto_service.py` - HowtoInfo.type field + parsing
- `src/sspec/commands/howto.py` - --type filter on list_cmd
- `src/sspec/howto/write-dim-*.md` - 8 dimension howto cards
- `src/sspec/templates/skills/sspec-design/examples-*.md` - 3 scenario example files + root

### Durable Memory (Typed, Timestamped)
- [2026-03-17T20:00] [Alignment] spec.md is a "prediction contract" — user reads it to form expectations of execution result. Different changes need different prediction dimensions.
- [2026-03-17T20:00] [Decision] Dimensions delivered as typed howtos (not examples files) to avoid "template anchoring effect" — agents see building blocks, not fixed patterns to copy.
- [2026-03-17T20:00] [Decision] Old Presentation Rules split: Rules 3-4 (Scope Summary + Item Labeling) stay as Universal Rules in SKILL; Rules 1-2 (code blocks + ASCII diagrams) move to dimension howto cards.
- [2026-03-17T20:00] [Decision] Template files not split — single `change/spec.md` with updated comment. Agent decides dimensions at design time, not at `sspec change new` time.
- [2026-03-17T20:00] [Decision] howto system gains `type` field (optional, backward compatible) + `--type` filter on `sspec howto list`.
- [2026-03-17T22:00] [VitalFinding] examples-root.md had stale Rule 1-4 references — caught by subagent audit, fixed.
- [2026-03-17T22:22] [Decision] Keep starter dimension combinations and a concise summary of the old code-block / ASCII-diagram hard rules in the main SKILL so weaker agents keep a safe default path without giving up the new dimension model.
- [2026-03-17T22:37] [VitalFinding] A second subagent audit still flags three non-trivial risks: examples use path forms that drift from current `.sspec/...` reference rules, the new prompt set no longer demonstrates the large-change `reference/design.md` path, and an unrelated `sspec-research` SKILL edit (`Grill User`) sits inside the same diff and conflicts with the repo's low-friction alignment posture.
- [2026-03-17T22:56] [Decision] Follow-up fixes accepted: simple-change threshold is now `<=3 files`, examples use `.sspec/...` reference paths, complex-change scaffolding explicitly demonstrates `reference/design.md`, Impact Map is conditional rather than quasi-default, and research-stage ambiguity handling lives in Exit Criteria instead of an aggressive questioning block.
- [2026-03-17T23:09] [VitalFinding] Post-commit subagent audit says the change is now "closer to Pareto": no substantive runtime defects remain, prior coverage gaps are closed, and remaining issues are minor prompt-surface nits (wrong batch HOWTO syntax in `sspec-design` SKILL and some Behavioral Spec examples that omit the companion explanatory text encouraged by the dimension card).
- [2026-03-17T23:58] [Decision] Final polish applied: batch HOWTO syntax in `sspec-design` SKILL now matches the documented `sspec howto read <n1> <n2>` form, and the remaining Behavioral Spec examples now include a one-line explanation under each diagram to match the card's own writing rule.

## Session Log (Append-Only)

### 2026-03-17T23:58 [work-log] Minor prompt-surface polish

**Accomplished**
- Fixed the batch HOWTO read example in `src/sspec/templates/skills/sspec-design/SKILL.md`
- Added companion explanatory text under the remaining Behavioral Spec diagrams in `src/sspec/templates/skills/sspec-design/examples-feature.md` and `src/sspec/templates/skills/sspec-design/examples-root.md`
- Reinstalled, synced templates, and smoke-tested `sspec howto read write-dim-interface-contract write-dim-behavioral-spec` both in-repo and in a fresh sandbox init

**Next**
- Ready for optional final commit if user wants to keep the handover note together with the prompt-surface polish

### 2026-03-17T23:09 [review-log] Post-commit independent audit

**Accomplished**
- Committed audit-follow-up fixes as `0057de8` (`🐛 fix(design): tighten prompt guidance after audit`)
- Ran 3 fresh independent subagent audits against the full change diff `d2d496efc7e92ddcf52c43d68eca3b091d9f7200..HEAD`

**Key findings**
- Runtime/code side: no substantive defects found; previous `howto list --type` coverage gaps are now closed
- Product judgment improved from `not Pareto` to `closer to Pareto`
- Remaining issues are minor only:
  - `src/sspec/templates/skills/sspec-design/SKILL.md` batch HOWTO example uses non-standard syntax (`sspec howto write-dim-<n1> write-dim-<n2>`) instead of the documented batch-read form
  - Some `Behavioral Spec` examples show diagrams without the extra explanatory text recommended by `write-dim-behavioral-spec`

**Next**
- Optional polish only: fix the batch HOWTO command example and add one-line explanatory text under the remaining Behavioral Spec diagrams

### 2026-03-17T22:56 [work-log] Audit follow-up implementation

**Accomplished**
- Made `### Key Design` scale-aware in both template comment and `sspec-design` SKILL (`<=3` simple, `4-15` medium, `>15` complex with `reference/design.md`)
- Demoted Impact Map from hidden-default language to a conditional companion dimension
- Aligned example reference paths to `.sspec/...` and added a large-change variant showing `reference/design.md`
- Reworked `sspec-research` ambiguity handling into Exit Criteria and removed the `Grill User` block
- Added builtin/rich coverage for `howto list --type`
- Re-ran lint, reinstall, template sync, focused pytest, rich HOWTO smoke test, and sandbox `sspec project init`

**Next**
- User review on whether the prompt surface now feels both flexible and safe for weaker agents

### 2026-03-17T22:37 [review-log] Subagent audit round 2

**Accomplished**
- Ran 3 independent subagent audits against `git diff d2d496efc7e92ddcf52c43d68eca3b091d9f7200..HEAD`
- Covered code/runtime behavior, prompt/RULE design, and product-level Pareto impact

**Key findings**
- Prompt/RULE risk: examples still use `requests/...` / `changes/...` style paths instead of the current `.sspec/...` convention, which weak models may copy into invalid references
- Prompt scaffolding risk: the new scenario examples removed the old explicit complex-change example, so the `>15 files -> reference/design.md` pattern is now underspecified
- Scope-control risk: the diff includes an unrelated `src/sspec/templates/skills/sspec-research/SKILL.md` edit (`Grill User`) that pushes agent behavior toward over-questioning
- Runtime/test quality is otherwise solid; remaining code-side issue is a low-priority coverage gap for builtin typed HOWTOs / rich output

**Next**
- Decide whether to fix the three prompt-surface issues now or keep this change as a strong-but-not-Pareto improvement

### 2026-03-17T22:22 [work-log] Review follow-up polish

**Accomplished**
- Added starter dimension combinations to `sspec-design` SKILL for feature/bugfix, refactor, docs/template/protocol, and migration/compatibility shapes
- Reintroduced a concise summary of the code-block / ASCII-diagram hard constraints in the main SKILL
- Renamed residual `examples-root.md` sub-change headings to `Interface Contract` / `Behavioral Spec`
- Added `howto list --type` coverage in `tests/test_howto_command.py`
- Re-ran install/sync, focused pytest, direct HOWTO smoke test, and sandbox `sspec project init`

**Next**
- User review on whether the added defaults improve the design workflow without reintroducing rigidity

### 2026-03-17T22:00 [work-log] Subagent audit fixes

**Accomplished**
- Ran 3 subagent audits (Python code, examples/cards, SKILL/template)
- Fixed C1: examples-root.md stale Rule 1-4 references
- Fixed W1-code: whitespace-only type → None normalization
- Fixed W3-code: better message when --type filter matches nothing
- Fixed W1-root: sub-change guidance uses dimension-neutral language
- Fixed W2-SKILL: added note to read dimension howto writing norms
- Fixed S1/S2/S3: type annotation, Step 4 wording, Behavioral Spec pairs

**Next**
- Change is REVIEW → user satisfied → handover + close

### 2026-03-17T21:00 [work-log] Implementation complete

**Accomplished**
- Phase 1: Added `type` field to HowtoInfo + `--type` filter on howto list
- Phase 2: Created 8 dimension howto cards (write-dim-*)
- Phase 3: Rewrote SKILL Step 3A with dimension menu + universal rules
- Phase 4: Split examples-single.md into examples-feature/docs/refactor.md
- Phase 5: Updated spec.md template Key Design comment
- Phase 6: Sync + smoke test passed (lint clean, init produces updated template)

**Next**
- Subagent audit on full diff

### 2026-03-17T20:28 [work-log] Design phase

**Accomplished**
- Discussed design direction with user: prediction contract framing, dimension menu, howto delivery
- Created change from request, filled spec.md with 7 change items (A-G)
- User approved design

**Next**
- Plan and implement
