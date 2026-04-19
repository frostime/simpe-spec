---
change: "add-prompt-assemble-tool"
created: 2026-04-19T16:36:58
---

# Design: add-prompt-assemble-tool

## Interface Contract

```python
PromptSourceType = Literal['file', 'file-chunk', 'shell', 'file-tree', 'glob']
PromptOutputFormat = Literal['hybrid-headers']
PromptFenceStyle = Literal['````']

class PromptSource(TypedDict, total=False):
    type: PromptSourceType
    label: str

    path: str              # file / file-chunk / file-tree root
    glob: str              # glob source pattern
    start: int             # file-chunk inclusive start line
    end: int               # file-chunk inclusive end line

    command: str           # shell source command string
    cwd: str               # optional shell working directory

    depth: int             # file-tree depth
    no_gitignore: bool     # optional file-tree override
    dirs_only: bool        # optional file-tree override

class PromptPreset(TypedDict, total=False):
    name: str
    description: str
    output_format: Literal['hybrid-headers']
    sources: list[PromptSource]

@dataclass(frozen=True, slots=True)
class ResolvedPromptBlock:
    kind: PromptSourceType
    label: str
    meta: dict[str, str]
    body: str

@dataclass(frozen=True, slots=True)
class PromptRunResult:
    output_text: str
    output_path: Path | None
    preset_path: Path | None
    block_count: int
```

CLI surface:

```text
sspec tool prompt [--add-file PATH] [--add-chunk PATH:START-END]
                  [--add-shell COMMAND] [--add-tree PATH] [--add-glob PATTERN]
                  [--from-preset NAME|PATH] [--to-preset NAME|PATH]
                  [--output FILE] [--dry-run] [--allow-shell] [--prompt]

sspec tool prompt --add-file src/sspec/commands/tool.py --add-shell "git status"
sspec tool prompt --add-chunk src/sspec/core.py:190-240 --add-tree src/sspec/builtin_tools
sspec tool prompt --from-preset review --add-shell "uv run pytest tests/test_tool_command.py" --allow-shell
sspec tool prompt --add-file src/sspec/commands/tool.py --to-preset tool_context
sspec tool prompt                 # no args => interactive
```

Notes:
- inline `--add-*` flags are first-class runtime inputs.
- `--from-preset` loads reusable sources before inline sources.
- `--to-preset` writes the merged runtime source list after validation.
- `--dry-run` suppresses file write + editor open and prints assembled text.
- V1 only ships `hybrid-headers`; future formats can extend `PromptOutputFormat`.

## Source Definition Model

Runtime sources can come from three places:

```text
preset sources
  + inline --add-* sources
  + interactive sources
        └── merged ordered list → validate → execute → render → optional export preset
```

Inline flag grammar:

| Flag | Source shape | Example |
|------|--------------|---------|
| `--add-file PATH` | `{type: file, path}` | `--add-file src/sspec/cli.py` |
| `--add-chunk PATH:START-END` | `{type: file-chunk, path, start, end}` | `--add-chunk src/sspec/core.py:190-240` |
| `--add-shell COMMAND` | `{type: shell, command}` | `--add-shell "git status --short"` |
| `--add-tree PATH` | `{type: file-tree, path}` | `--add-tree src/sspec/builtin_tools` |
| `--add-glob PATTERN` | `{type: glob, glob}` | `--add-glob "src/sspec/builtin_tools/*.py"` |

Preset example:

```yaml
name: review
output_format: hybrid-headers
sources:
  - type: file
    path: src/sspec/commands/tool.py
    label: tool command

  - type: file-chunk
    path: src/sspec/services/cmd_service.py
    start: 1
    end: 80
    label: cmd service excerpt

  - type: file-tree
    path: src/sspec/builtin_tools
    depth: 2
    label: builtin tools tree

  - type: shell
    command: git status --short --branch
    label: git status
```

Validation rules:

| Source type | Required fields | Optional fields |
|-------------|-----------------|-----------------|
| `file` | `path` | `label` |
| `file-chunk` | `path`, `start`, `end` | `label` |
| `shell` | `command` | `label`, `cwd` |
| `file-tree` | `path` | `label`, `depth`, `dirs_only`, `no_gitignore` |
| `glob` | `glob` | `label` |

Shared constraints:
- relative paths resolve from project root.
- `file-chunk` line range is inclusive and must satisfy `1 <= start <= end`.
- `glob` expands to files only and renders each match as its own file block.
- shell execution in non-interactive mode requires `--allow-shell`.
- `--to-preset` writes UTF-8 YAML under `.sspec/prompts/<name>.yml` when given a bare name.

## Output Contract

Each rendered block uses a stable envelope with an explicit meta/content split:

```text
========== BEGIN FILE ==========
---
label: tool command
path: src/sspec/commands/tool.py
kind: file
content_format: fenced
fence: "````"
---
````
<original file content>
````
========== END FILE ==========
```

Examples by kind:

```text
========== BEGIN FILE CHUNK ==========
---
label: cmd service excerpt
path: src/sspec/services/cmd_service.py
range: L1-L80
kind: file-chunk
content_format: fenced
fence: "````"
---
````
<original excerpt>
````
========== END FILE CHUNK ==========
```

```text
========== BEGIN SHELL OUTPUT ==========
---
label: git status
command: git status --short --branch
cwd: H:/SrcCode/playground/sspec
kind: shell
content_format: fenced
fence: "````"
---
````
<captured stdout+stderr summary>
````
========== END SHELL OUTPUT ==========
```

```text
========== BEGIN FILE TREE ==========
---
label: builtin tools tree
path: src/sspec/builtin_tools
depth: 2
kind: file-tree
content_format: fenced
fence: "````"
---
````
<tree text>
````
========== END FILE TREE ==========
```

Design choices:
- metadata uses YAML frontmatter for an unmistakable block-level meta area.
- body content always sits inside a four-backtick fence so metadata and payload are visually and syntactically separated.
- four backticks reduce collision risk when body content already contains triple-backtick fences.
- section titles stay type-specific so Web Agent / LLM can segment content quickly.
- default file extension is `.prompt.txt` to avoid markdown rendering ambiguity.

## Behavioral Spec

### Inline-first flow

```text
CLI args
  ├── parse --from-preset sources when present
  ├── parse all --add-* sources in command order
  └── merge source list
        └── validate source schema
              ├── --to-preset present → write merged source list as preset
              └── execute sources
                    ├── file       → read full file
                    ├── file-chunk → read inclusive line range
                    ├── file-tree  → render tree text
                    ├── glob       → expand matches → read each file
                    └── shell      → require --allow-shell → run command
                          └── render blocks
                                ├── dry-run   → print to stdout
                                └── default   → write .sspec/tmp/*.prompt.txt → open editor
```

### Interactive flow

```text
sspec tool prompt   (no args)
  └── choose source type
        └── collect source fields
              ├── path-like fields use interactive path prompt/completion
              ├── shell source asks command and optional cwd
              └── append source to in-memory source list
                    └── repeat until done
                          ├── optional save preset (--to-preset or prompt)
                          └── execute assembly
                                ├── shell sources require per-item confirm
                                └── write tmp prompt unless --dry-run
```

### Shell safety

```text
non-interactive shell source
  ├── --allow-shell absent  → fail fast with actionable message
  └── --allow-shell present → execute all shell sources

interactive shell source
  ├── confirm each shell block before execution
  ├── declined block        → render skipped marker text
  └── confirmed block       → execute and capture output
```

Skipped shell block rendering:

```text
========== BEGIN SHELL OUTPUT ==========
---
label: build summary
command: uv run pytest tests/test_tool_command.py
kind: shell
status: skipped-by-user
content_format: fenced
fence: "````"
---
````
[SHELL BLOCK SKIPPED]
````
========== END SHELL OUTPUT ==========
```

## Structural Blueprint

```text
src/sspec/
├── builtin_tools/
│   └── prompt.py            # click wiring, prompt text, inline flags, interactive entry
├── services/
│   └── prompt_service.py    # source model, preset import/export, source execution, rendering, tmp write
└── commands/
    └── tool.py              # register prompt builtin

tests/
├── test_prompt_service.py   # schema, inline parsing helpers, render, shell safety, output path
└── test_tool_command.py     # CLI smoke + prompt flag + inline run + preset export/import
```

Responsibility split:
- `builtin_tools/prompt.py` owns Click options, option-order handling, questionary-driven interactive UX, and console messaging.
- `services/prompt_service.py` owns reusable source normalization, preset I/O, execution logic, and output rendering.
- `commands/tool.py` remains a thin registration shell.

## Scope Mapping

| File | Design Work |
|------|-------------|
| `src/sspec/builtin_tools/prompt.py` | Add tool metadata, inline `--add-*` flags, preset flags, questionary flow, and final invoke path |
| `src/sspec/services/prompt_service.py` | Add source parsing/validation, preset import/export, source execution, hybrid-header rendering, tmp output creation |
| `src/sspec/commands/tool.py` | Register `prompt` builtin tool |
| `.sspec/spec-docs/builtin-tools.md` | Document `prompt` tool contract, inline flags, preset directory, source types, and output format |
| `tests/test_prompt_service.py` | Validate schema rules, inline parsing, YAML-frontmatter + fenced-content rendering, glob expansion, shell gate, and tmp write behavior |
| `tests/test_tool_command.py` | Validate CLI prompt help, inline dry-run, preset export/import, and command registration |
