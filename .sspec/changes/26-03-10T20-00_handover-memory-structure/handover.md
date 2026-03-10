# Handover: handover-memory-structure

**Updated**: 2026-03-10T21:23

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Reassess the default `handover.md` memory structure so stable memory is easier to maintain and
less likely to duplicate session-state content. The immediate focus is the overlap between
`Working Memory -> Decisions / Notes` and `Session Log`.

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `cdabbc4ab4858727f3d77a4f15b1b535252bf48c`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main [ahead 11]
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->
- `src/sspec/templates/change/handover.md` - single-change handover template under review.
- `src/sspec/templates/change-root/handover.md` - root-change variant; useful comparison point for
  coordination-specific memory structure.
- `src/sspec/templates/skills/sspec-handover/SKILL.md` - current rules that teach agents what goes
  into Working Memory vs Session Log.
- `src/sspec/howto/write-handover.md` - concise operational guide; will need to match any template
  changes.
- `src/sspec/services/change_service.py` - resume/dashboard parsing depends on `Session Log`, not on
  Memory subsection names.
- `.sspec/changes/archive/26-03-06T00-34_handover-template-v2/spec.md` - prior rationale for the
  stable-vs-volatile split.
- `.sspec/changes/26-03-10T20-00_handover-memory-structure/reference/analysis.md` - current
  research summary, duplication patterns, and option comparison.

### Decisions (Timestamped)
<!-- Timestamp every entry (minute precision).
- [2026-03-06T20:39] **Decision** - Redis over Memcached
  **Why**: Need per-key TTL + persistence -->
- [2026-03-10T20:23] **Decision** - Use `Durable Memory (Typed, Timestamped)` as the target
  section name in the design and plan.
  **Why**: It keeps the merged memory purpose explicit while distinguishing cross-session memory
  from the append-only `Session Log`.
- [2026-03-10T20:12] **Decision** - Prefer a single typed durable-memory section with recommended
  canonical types plus rare agent-defined exceptions.
  **Why**: This keeps the structure consistent and scannable without blocking special-case memory
  entries.
- [2026-03-10T20:01] **Decision** - Track this as a single change rather than a root change.
  **Why**: The likely work stays within a small template/doc surface and does not need parallel
  sub-changes.

### Notes (Timestamped)
<!-- Gotchas, edge cases, risks, verification shortcuts. Timestamp every entry.
Project-wide items -> ALSO append to project.md Notes. -->
- [2026-03-10T21:23] The HOWTO split now gives cleaner separation of concerns: SKILL owns the
  lifecycle contract, while focused HOWTOs own concrete writing jobs and obsolete-memory handling.
- [2026-03-10T21:18] User approved a scope refinement: instead of growing `write-handover`, split
  handover HOWTOs by job so they stop overlapping with the phase-level `sspec-handover` SKILL.
- [2026-03-10T21:07] User explicitly does not want the active change handover back-migrated to the
  new durable-memory structure; this change record may stay on the old `Decisions` / `Notes`
  layout as a deliberate exception.
- [2026-03-10T21:07] Chosen obsolete-memory policy: default to marking entries obsolete with a
  timestamp so history remains visible; only pure noise, accidental duplicates, or placeholder
  residue should be deleted outright.
- [2026-03-10T20:59] Subagent audit found one concrete consistency issue: this active change's own
  `handover.md` still uses the old `Decisions` / `Notes` structure even though the templates and
  guidance now teach `Durable Memory (Typed, Timestamped)`.
- [2026-03-10T20:59] Audit also suggested two non-blocking follow-ups: restore explicit obsolete
  entry guidance in `write-handover.md`, and consider one regression/clarity improvement around
  parser safety or root-type choice examples.
- [2026-03-10T20:41] Follow-up validation passed after splitting recommended type vocabularies:
  single/sub and root-generated handovers now show different durable-memory type hints in
  `tmp/test_handover_memory_structure/`.
- [2026-03-10T20:36] Review feedback identified a real design gap: root-change handovers should not
  inherit the same recommended durable-memory types as single/sub changes because their durable
  knowledge is coordination-oriented.
- [2026-03-10T20:30] Validation passed with `uv pip install -e .`, `uv run sspec project update`,
  and sandbox generation in `tmp/test_handover_memory_structure/` for both single and root
  changes.
- [2026-03-10T20:23] Current plan uses three phases: template edits, guidance alignment, then
  template sync plus sandbox validation.
- [2026-03-10T20:20] Design draft now lives in `spec.md`; planning is intentionally blocked until
  the user explicitly approves the drafted section name, type set, and promotion rule.
- [2026-03-10T20:09] User is interested in collapsing `Decisions` / `Notes` into one typed memory
  section with entries shaped like `[time] [type] [content]`.
- [2026-03-10T20:01] The current stable-vs-volatile split is conceptually right, but `Notes` is so
  broad that real usage turns it into a catch-all bucket.
- [2026-03-10T20:01] `change_service.py` currently parses `Updated`, `Session Log`, and `Next`; a
  Memory-only restructure should be low-risk if `Session Log` stays compatible.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-10T21:23 [work-log] split handover howtos and validate discovery flow

**Accomplished**
- Converted `src/sspec/howto/write-handover.md` into a lightweight router instead of a second
  handover mini-skill.
- Added focused HOWTOs: `src/sspec/howto/write-handover-log.md`,
  `src/sspec/howto/write-handover-memory.md`, and `src/sspec/howto/handle-obsolete-memory.md`.
- Updated `src/sspec/templates/skills/sspec-handover/SKILL.md` to point to the focused HOWTOs only
  where extra detail is useful.
- Updated `src/sspec/howto/handover-checklist.md` to use Durable Memory terminology.
- Reinstalled/synced templates and verified `sspec howto list` plus targeted `sspec howto ...`
  reads for the new handover HOWTO set.
- Returned the change to `REVIEW` and marked the HOWTO refactor tasks complete.

**Next**
- Ask the user to review the new handover HOWTO topology and whether the split feels clean enough.
- If accepted, the change can move to `DONE`; otherwise adjust naming/scope of the focused HOWTOs.

**Notes** (optional)
- The active change handover still intentionally stays on the legacy `Decisions` / `Notes`
  structure by user exception.

### 2026-03-10T21:18 [user-feedback] split handover howtos by job instead of growing write-handover

**Accomplished**
- User approved a cleaner HOWTO direction: keep `sspec-handover` as the lifecycle contract and move
  detailed write guidance into smaller, focused HOWTOs.
- Chosen HOWTO shape: `write-handover` becomes a router, with focused follow-ups such as
  `write-handover-log`, `write-handover-memory`, and `handle-obsolete-memory`.
- Reopened implementation to update design/tasks before editing the HOWTO set.

**Next**
- Refactor the current handover HOWTO into the focused set.
- Update `sspec-handover` to point to the new HOWTOs only where extra detail is actually useful.

**Notes** (optional)
- This should reduce SKILL/HOWTO overlap without weakening the handover lifecycle guidance.

### 2026-03-10T21:07 [user-feedback] keep active handover legacy and refine examples/obsolete policy

**Accomplished**
- Got explicit direction from the user not to back-migrate this active change handover to the new
  durable-memory structure.
- Added restrained extra memory-type examples where they help most: a small root example in the
  template, core chooser guidance in the SKILL, and fuller progressive examples in the HOWTO.
- Chose and documented the obsolete-memory policy: mark obsolete by default, delete only obvious
  noise/duplicates/placeholders.
- Re-synced templates and regenerated sandbox changes to confirm the updated guidance still renders
  correctly.
- Returned the change to `REVIEW` and marked follow-up tasks complete.

**Next**
- Ask the user to review the final wording, especially the obsolete-memory policy and the amount of
  example detail in SKILL vs HOWTO.
- If accepted, the change can move to `DONE`.

**Notes** (optional)
- This closes the audit gap by explicit product decision rather than by forcing the active change
  record into the new structure mid-stream.

### 2026-03-10T20:59 [work-log] run subagent audit on staged handover-memory diff

**Accomplished**
- Read `sspec howto make-subagent-audit` and `sspec howto review-git-baseline` before auditing.
- Ran two independent subagent audits against the staged diff for the handover-memory change.
- Consolidated the audit output: one blocking consistency issue and two non-blocking nits.
- Reopened the change to `DOING` and added follow-up tasks so the review findings are tracked.

**Next**
- Fix the active change handover so it matches the new durable-memory structure.
- Decide whether to take the optional follow-ups: restore obsolete-entry guidance in the HOWTO and
  add either a parser-focused regression or extra root-type selection guidance.

**Notes** (optional)
- The stronger audit result still agrees with the overall direction; the issue is consistency and
  polish, not a fundamental design failure.

### 2026-03-10T20:41 [work-log] refine root durable memory vocabulary and revalidate

**Accomplished**
- Updated the design so single/sub and root handovers keep the same durable-memory section shape but
  use different recommended type vocabularies.
- Changed the root template to recommend coordination-oriented types: `CoordinationDecision`,
  `Dependency`, and `CrossChangeFinding`, alongside shared types like `Alignment`, `Constraint`, and
  `Risk`.
- Updated `sspec-handover` guidance and `write-handover` HOWTO to explain the single-vs-root type
  split explicitly.
- Reinstalled/synced templates again and generated fresh sandbox changes to verify the new single
  and root hints both render correctly.
- Returned the change to `REVIEW` and marked feedback follow-up tasks complete.

**Next**
- Ask the user to review whether the root-specific type set now better matches coordination-style
  handovers.
- If accepted, the change can move to `DONE`; if not, iterate on the root vocabulary again.

**Notes** (optional)
- The shared section name still works; the main fix was giving root changes their own recommended
  semantic vocabulary.

### 2026-03-10T20:36 [user-feedback] root changes need different recommended memory types

**Accomplished**
- User reviewed the first implementation and pointed out that single and root changes have different
  durable-memory semantics.
- Confirmed the current root template reused the single-change recommended type set too literally.
- Reopened the change for a design/implementation tightening pass focused on root-specific type
  recommendations.

**Next**
- Refine the design so root handovers use coordination-oriented recommended types.
- Update templates/guidance and re-run validation for both single and root change generation.

**Notes** (optional)
- The section shape can stay shared; the feedback is about scope-specific vocabulary, not about
  removing typed durable memory itself.

### 2026-03-10T20:30 [work-log] implement typed durable memory and validate templates

**Accomplished**
- Updated `src/sspec/templates/change/handover.md` and
  `src/sspec/templates/change-root/handover.md` to use one `Durable Memory (Typed, Timestamped)`
  section instead of split `Decisions` / `Notes` buckets.
- Updated `src/sspec/templates/skills/sspec-handover/SKILL.md` and
  `src/sspec/howto/write-handover.md` to teach typed durable memory, canonical types, and the
  durable-vs-batch promotion rule.
- Reinstalled the package and ran `uv run sspec project update`, which refreshed the self-hosted
  `sspec-handover` skill copy.
- Created sandbox project `tmp/test_handover_memory_structure/` and generated both single and root
  changes to confirm the new handover structure renders correctly.
- Updated `spec.md` to `REVIEW` and marked all planned tasks complete.

**Next**
- Ask the user to review the new template/guidance wording and confirm whether the chosen section
  name and type set feel right in practice.
- If feedback arrives, return to implementation for a tightening pass; otherwise the change can move
  toward DONE/commit.

**Notes** (optional)
- `change_service.py` did not require edits because `Session Log` structure stayed intact.

### 2026-03-10T20:23 [work-log] record design approval and draft plan

**Accomplished**
- Received design approval in conversation and continued into planning.
- Drafted `.sspec/changes/26-03-10T20-00_handover-memory-structure/tasks.md` with three phases:
  template changes, writing-guidance updates, and sync/validation.
- Kept the plan focused on template-source edits first, with `uv pip install -e .` and
  `uv run sspec project update` deferred to the validation phase.

**Next**
- Get lightweight confirmation that the drafted task breakdown looks right.
- If confirmed, begin implementation with Phase 1 template edits.

**Notes** (optional)
- The plan intentionally avoids parser changes because the approved design keeps `Session Log`
  compatibility intact.

### 2026-03-10T20:20 [work-log] draft design and stop at design gate

**Accomplished**
- Drafted `.sspec/changes/26-03-10T20-00_handover-memory-structure/spec.md` with the merged typed
  durable-memory design.
- Defined the recommended canonical type set and the "rare custom type" escape hatch.
- Kept `Session Log` compatibility explicit so current resume/dashboard parsing does not need to
  change.
- Created a design-alignment ask record at `.sspec/asks/260310201917_handover_memory_design.yml`
  and prompted it.

**Next**
- Get explicit user approval or revisions for the drafted design.
- Only after that, write `tasks.md` for template/skill/howto updates.

**Notes** (optional)
- The `sspec ask prompt` result returned the template placeholder instead of a meaningful answer in
  this host flow, so direct user confirmation is still needed in conversation.

### 2026-03-10T20:12 [user-feedback] prefer recommended types with flexible escape hatch

**Accomplished**
- Asked the user whether typed memory entries should use fixed or freeform labels.
- Got alignment on the preferred model: recommended canonical types, but allow agent-defined types
  in special scenarios.
- Captured this as the current design direction for the merged memory section.

**Next**
- Draft the design around one merged typed memory section plus a small canonical taxonomy.
- Define when agents may introduce a custom type and how to keep it rare/non-noisy.

**Notes** (optional)
- This is effectively a controlled-flexibility model rather than strict enum-only validation.

### 2026-03-10T20:09 [user-feedback] propose one typed memory section

**Accomplished**
- Received a new direction from the user: merge `Decision` / `Notes` style memory into one section.
- Captured the preferred entry shape as typed records such as `[time] [type] [content]`.
- Noted example durable types the user cares about: `Alignment`, `VitalFindings`, `Constraints`.

**Next**
- Evaluate this typed-single-section design against the earlier section-based options.
- Align on whether types should be a small canonical set or freeform labels before drafting `spec.md`.

**Notes** (optional)
- This direction likely solves the section-boundary confusion more directly than a simple `Notes`
  rename.

### 2026-03-10T20:01 [work-log] research current handover duplication and create change

**Accomplished**
- Read `.sspec/project.md` for repo conventions and template-ground-truth rules.
- Reviewed current single/root handover templates, handover HOWTO, and `sspec-handover` skill.
- Sampled recent handovers to inspect real usage patterns and overlap between Memory and Session
  Log.
- Confirmed the current dashboard/resume parser depends on `Session Log`, not Memory subsection
  names.
- Created change `26-03-10T20-00_handover-memory-structure` and wrote research notes in
  `reference/analysis.md`.

**Next**
- Align with the user on the preferred target shape for durable memory.
- Then draft `spec.md` around the chosen direction and only later touch templates/skill/howto.

**Notes** (optional)
- The strongest duplication source is not `Session Log` itself; it is the overly broad meaning of
  Memory `Notes`.
