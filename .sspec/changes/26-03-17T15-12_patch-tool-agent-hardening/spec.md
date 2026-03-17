---
name: patch-tool-agent-hardening
status: REVIEW
type: ""
change-type: single
created: 2026-03-17T15:12:39
reference:
  - source: ".sspec/spec-docs/builtin-tools.md"
    type: "doc"
    note: "Builtin tool architecture and current tool inventory"
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# patch-tool-agent-hardening

## A. Problem Statement

`sspec tool patch` currently mixes three agent-hostile behaviors that slow recovery after a failed patch batch: patch targets only accept project-root-relative paths, failed retries are reported with coarse `SEARCH not found` style errors, and non-`.sspec` runs still default their failed output into a `.sspec/tmp/...` layout. In practice this causes repeated manual inspection, makes repeated apply operations look like hard failures instead of `already applied`, and keeps the tool less consistent than the newer `write` / `fileinfo` helpers that already support absolute paths and non-`.sspec` usage.

For the next round, the patch tool needs to behave like a reusable general CLI helper: accept relative or absolute file targets, support agent-friendly patch input via `--stdin`, classify retry/failure states precisely enough for fast correction, and emit one markdown failure bundle that is both readable and directly reusable as the next patch input.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution

### Approach

Keep the existing SEARCH/REPLACE patch format and matching behavior as the core contract, but harden the command around that core. The command should accept three practical input modes for agents and humans (`PATCH_FILE` / `--file`, `--stdin`, `--input`), parse patch headers with a more robust path + optional line-range parser, and classify non-success outcomes into actionable states rather than collapsing them into generic match failures.

For failed patch handling, separate diagnostics from retry content. The command prints rich terminal summaries with patch source line numbers, target file line numbers, and a short patch preview, while it writes a single markdown failure bundle that contains explanatory prose plus fenced `patch` blocks that can be fed back into `sspec tool patch` after small edits. This keeps the failure artifact readable without breaking the existing parser's ability to scan valid patch blocks out of mixed-content markdown.

### Key Design

#### Interface Design

```python
# src/sspec/builtin_tools/apply_patch.py
PatchOutcomeStatus = Literal[
    'applied',
    'already_applied',
    'search_not_found',
    'search_ambiguous',
    'replace_ambiguous',
    'search_replace_coexist',
    'invalid_path',
    'missing_file',
    'not_a_file',
    'invalid_line_range',
    'out_of_range',
    'parse_error',
    'write_error',
    'no_change_patch',
]

@dataclass
class PatchApplyResult:
    patch: PatchBlock | None
    success: bool
    status: PatchOutcomeStatus
    error: str | None = None
    match_mode: str | None = None
    match_line: int | None = None
    related_lines: list[int] | None = None
    source_line_start: int | None = None
    search_line_count: int = 0
    replace_line_count: int = 0
```

```python
# src/sspec/builtin_tools/apply_patch.py
def parse_patch_header(header: str, *, project_root: Path) -> tuple[Path, str, tuple[int | None, int | None] | None]:
    """Parse '# <path>[:<range>]' with absolute/relative path support."""

def parse_line_range(text: str) -> tuple[int | None, int | None]:
    """Support L10-L20, L10-, -L20, plus legacy 10-20 compatibility."""
```

```python
# src/sspec/builtin_tools/apply_patch.py
@group.command(name='patch')
@click.option('--stdin', 'stdin_mode', is_flag=True, help='Read patch text from stdin.')
def patch_command(...):
    """Input sources are PATCH_FILE / --file / --stdin / --input, mutually exclusive."""
```

#### Data Flow

```text
patch input (PATCH_FILE | --file | --stdin | --input)
  │
  ├── load_patch_text()                 → one explicit source, `--prompt` bypasses all validation
  ├── parse_patches()                   → scan markdown/plaintext for valid patch blocks
  │     ├── parse_patch_header()        → path + optional line-range
  │     └── validate_target()           → absolute/relative file resolution, existence, type
  ├── apply_patch()                     → exact search → loose search → replace-state checks
  │     ├── apply replacement           → status `applied`
  │     ├── detect already applied      → status `already_applied`
  │     └── classify ambiguity/failure  → actionable non-success status + line numbers
  ├── print_result_summary()            → file path, patch line, target line(s), reason, preview
  └── write_failed_bundle()             → one markdown file with failed patch sections
        ├── .sspec/tmp/... when inside sspec project
        └── system temp file otherwise
```

#### Key Logic

**Fix A: Input and path model** — Add `--stdin` as the agent-friendly non-interactive input path. Keep `PATCH_FILE` / `--file` for file-based input and `--input` as a human fallback. Patch headers accept both absolute and relative file paths; relative paths remain rooted at the detected project root (or `cwd` when no `.sspec` project exists).

**Fix B: Header and line-range parsing** — Replace the single regex-only file header parse with a helper that can distinguish Windows drive letters from `:Lx-Ly` suffixes. Support canonical ranges `L10-L20`, `L10-`, `-L20`, while still accepting legacy `10-20` syntax for backward compatibility. Open-ended ranges resolve against the current file length at apply time.

**Fix C: Retry-aware failure classification** — When `SEARCH` is not found, run the same scoped matching process against `REPLACE` before declaring failure. This allows the tool to distinguish `already_applied`, `replace_ambiguous`, `search_replace_coexist`, and true `search_not_found` cases. `already_applied` and `no_change_patch` count as non-fatal outcomes so rerunning a patch batch does not fail just because some edits were already present.

**Fix D: Diagnostics and failed bundle output** — Emit a per-patch terminal summary that includes patch source line (`Patch line: L...`), target line or candidate lines (`Target line(s): ...`), reason, and a truncated SEARCH/REPLACE preview. Save all failed patches into one markdown bundle. Each failed section contains readable explanation outside the code fence and the original patch inside a fenced `patch` block so the same file can be reused as future patch input after minor edits.

#### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/builtin_tools/apply_patch.py` | Add robust header parsing, `--stdin`, richer result statuses, retry detection, and markdown failure bundle generation |
| `tests/test_tool_command.py` | Add command-level coverage for `--stdin`, non-`.sspec` failed output behavior, and readable status summaries |
| `tests/test_apply_patch.py` | Add focused parser/application tests for absolute paths, open-ended line ranges, `already_applied`, and markdown bundle reuse |
| `.sspec/spec-docs/builtin-tools.md` | Update patch tool behavior, supported input modes, and failure artifact format |

<!-- @RULE: Accepted review-stage changes belong here as formal design.
If user feedback changes the current change's scope/design and the work still belongs to this change,
update A/B directly instead of leaving the accepted change only in handover.md.
If review history matters, add `### Review Amendments` under B as part of the design. -->

