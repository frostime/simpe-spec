---
name: add-howto-cli
status: REVIEW
type: ''
change-type: single
created: 2026-03-09 23:41:08
reference:
- source: .sspec/requests/26-03-09T23-23_add-howto-cli.md
  type: request
  note: Linked from request
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

# add-howto-cli

## A. Problem Statement
### Current Situation

sspec currently exposes durable guidance mainly through `AGENTS.md` and SKILL documents. This leaves a gap between repo-wide protocol and heavyweight skill workflows: small, focused rules have no dedicated home, causing 1-level disclosure to carry too much content and making progressive guidance harder to compose.

### User Requirement

Add a lightweight HOWTO document channel so users can read one narrowly scoped instruction at a time through `sspec howto <name>` or discover available entries with `sspec howto --list`. The mechanism must support both package-shipped HOWTOs and project-local HOWTOs under `.sspec/howto/`, and it should stay easy to extend as more sspec usage guidance gets split out later.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
Introduce HOWTO as a lightweight documentation registry dedicated to very small operational guides. Unlike SKILL, a HOWTO is not a capability bundle or workflow phase contract; it is a short markdown document that can be discovered, read, and optionally scaffolded from the CLI.

The implementation should mirror the successful parts of the existing skill/doc architecture without inheriting their extra lifecycle behaviors. A dedicated `howto_service` will own discovery, metadata parsing, duplicate detection, body loading, and new-file scaffolding; the CLI layer will only translate user intent into terminal output. This keeps future expansion cheap if sspec later adds validation, agent-facing HOWTO disclosure, or richer authoring helpers.

### Approach

Use `sspec howto` as an extensible command group with an implicit default read action. User ergonomics stay short — `sspec howto <name>` still works — while explicit subcommands remain available for growth: `sspec howto list`, `sspec howto read <name>`, and `sspec howto new <name>`. `sspec howto --list` should remain as a shorthand alias for the list action because that syntax is already part of the request.

Store official HOWTOs inside the package at `src/sspec/howto/` and user-authored HOWTOs inside `.sspec/howto/`. At runtime, the service scans both locations, parses markdown frontmatter, normalizes names into lookup keys, and merges the result into one logical registry. If two HOWTOs resolve to the same lookup key, the duplicate should not override silently; instead, sspec should emit a warning and skip the later conflicting entry.

Render HOWTO content as markdown without showing raw YAML frontmatter. For metadata, support the requested `desc` field and also accept `description` as an alias so HOWTO authoring stays consistent with existing sspec conventions. When `name` is omitted, fall back to the filename stem to keep local authoring forgiving.

### Key Design

### Interface Design

**Feat A: HOWTO document model** — add a small service-owned metadata model for discovery and resolution.

```python
@dataclass(frozen=True, slots=True)
class HowtoInfo:
  name: str
  lookup_key: str
  description: str
  path: Path
  source: Literal['builtin', 'project']
  file: str


@dataclass(frozen=True, slots=True)
class HowtoCatalog:
  items: tuple[HowtoInfo, ...]
  warnings: tuple[str, ...]


def parse_howto_metadata(howto_path: Path) -> dict[str, Any]: ...
def collect_howtos(sspec_root: Path) -> HowtoCatalog: ...
def resolve_howto(sspec_root: Path, name: str) -> tuple[HowtoInfo | None, tuple[str, ...]]: ...
def read_howto_body(howto_path: Path) -> str: ...
def create_project_howto(sspec_root: Path, name: str, description: str = '') -> Path: ...
```

`lookup_key` is the normalized internal match key derived from frontmatter `name` or filename stem. It is not user-facing terminology; it only exists so `Write-Handover`, `write-handover`, and `write_handover` can resolve consistently.

**Feat B: CLI contract** — implement the user-visible command as an extensible group with an implicit read fallback.

```python
class ImplicitReadGroup(click.Group):
  """Map `sspec howto <name>` to `sspec howto read <name>`."""


@click.group(cls=ImplicitReadGroup, invoke_without_command=True)
@click.option('--list', 'list_only', is_flag=True, help='List all HOWTO documents')
def howto(list_only: bool) -> None: ...


@howto.command(name='read')
@click.argument('name')
def read_cmd(name: str) -> None: ...


@howto.command(name='list')
def list_cmd() -> None: ...


@howto.command(name='new')
@click.argument('name')
def new_cmd(name: str) -> None: ...
```

Behavior contract:

```python
# Requested frontmatter shape (accepted)
meta = {
  'name': 'write-handover',
  'desc': 'Short guide for updating handover.md',
}

# Compatibility aliases (also accepted)
meta = {
  'name': 'write-handover',
  'description': 'Short guide for updating handover.md',
}
```

### Data Flow

```text
CLI Input
  │
  ├── dispatch `--list` / `list` / `read <name>` / implicit `<name>` / `new <name>`
  │
  ├── howto_service
  │   ├── scan `src/sspec/howto/*.md`        → builtin HOWTOs
  │   ├── scan `.sspec/howto/*.md`           → project HOWTOs
  │   ├── parse YAML frontmatter             → name/desc metadata
  │   ├── normalize to lookup key            → stable resolution
  │   └── detect duplicate key               → warning + skip later item
  │
  └── render result
      ├── list mode  → table(name, description, source)
      ├── read mode  → markdown body without frontmatter
      └── new mode   → scaffold `.sspec/howto/<name>.md`
```

**Note**: putting merge logic in the service keeps precedence and normalization rules testable without terminal I/O.

### Key Logic

**Registry normalization and duplicate safety**
- Normalize lookup keys from frontmatter `name`, then fall back to filename stem.
- Use lowercase kebab-style matching so `write-handover`, `Write-Handover`, and the same stem resolve to one logical entry.
- If two HOWTOs share the same lookup key, record a warning and skip the later entry instead of overriding silently.
- Scan builtin HOWTOs before project HOWTOs so collisions are reproducible and defaults remain authoritative.

**Output model**
- Default output should be agent-friendly plain text.
- `--format rich` should enable prettier terminal rendering for humans.
- `--list` and `list` should emit compact plain-text records by default, with rich table output only when formatting is requested.
- `sspec howto <name>` and `sspec howto read <name>` should emit plain-text metadata + markdown body by default, with rich panel rendering only when formatting is requested.
- Missing name without `--list` should raise a clear usage error.
- Unknown HOWTO name should raise a `ClickException` that nudges users toward `--list`.
- Duplicate-skip warnings should be surfaced before successful output so users notice conflicts.

**Authoring scaffold and packaging boundary**
- `sspec howto new <name>` should create `.sspec/howto/<name>.md` with minimal HOWTO frontmatter and body placeholder.
- The first version only scaffolds project HOWTOs; it does not manage builtin HOWTO creation.
- Official HOWTO docs belong in `src/sspec/howto/`, not `src/sspec/templates/`, because they are runtime package resources rather than project-scaffold templates.
- Project-local HOWTOs are read directly from `.sspec/howto/`; no install/sync pipeline is needed for the first version.

**Initial builtin HOWTO batch**
- This change should leave room for a first builtin HOWTO batch, but the exact initial topics should be confirmed with the user before implementation is finalized.
- Current batch: `write-howto`, `use-sspec-ask`, and `read-long-mdfile`.

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/cli.py` | Register the new `howto` command at the CLI root |
| `src/sspec/commands/howto.py` | Add `sspec howto <name>` / `sspec howto --list` command behavior |
| `src/sspec/services/howto_service.py` | Add HOWTO discovery, metadata parsing, merge, and body-loading logic |
| `src/sspec/core.py` | Add shared HOWTO path constants/helpers needed by service/command |
| `src/sspec/howto/*.md` | Add package-shipped builtin HOWTO documents |
| `tests/test_howto_command.py` | Add CLI behavior coverage for list, lookup, duplicate warnings, scaffolding, and error paths |
