---
change: "portable-mode-agent-resources"
created: 2026-05-09T20:59:30
---

# Design: portable-mode-agent-resources

## 1. CLI Contract

```text
sspec portable
sspec portable read <scope:slug>
```

| Command | Purpose | Project required | Writes files |
|---|---|---:|---:|
| `sspec portable` | Print portable Agent bootstrap + indexes | No | No |
| `sspec portable read rule:sspec` | Read rendered built-in sspec agent protocol with source metadata | No | No |
| `sspec portable read skill:sspec-design` | Read built-in SKILL.md with source metadata | No | No |
| `sspec portable read skill:sspec-design/examples-feature.md` | Read skill attachment with source metadata | No | No |
| `sspec portable read howto:write-memory` | Read built-in HOWTO with source metadata | No | No |
| `sspec portable read template:change/spec.md` | Read built-in template with source metadata | No | No |

No options in MVP. Keep the surface intentionally small.

## 2. Output Contract: `sspec portable`

`sspec portable` prints XML-like, Agent-readable bootstrap text. It assumes the consuming Agent may know nothing about sspec.

````xml
<sspec-portable schema="6.0">

<what_is_this>
sspec is a spec-driven working protocol for AI coding agents.
It provides:
- rules: general behavior for clarifying, designing, planning, implementing,
  reviewing, and aligning with the user;
- skills: task-specific instructions loaded only when relevant;
- templates: optional files used by full sspec projects to persist specs,
  tasks, memory, requests, and docs.

You are using sspec in portable mode.
Portable mode means: use sspec rules and skills as behavioral guidance,
but do not initialize or manage sspec project state in the current workspace.
</what_is_this>

<portable_constraints>
Unless the user explicitly asks to install or manage sspec in this project:
- do not run `sspec project init`;
- do not run `sspec change new`, `sspec request new`, `sspec doc new`, or `sspec skill dominate`;
- do not create `.sspec/`, `AGENTS.md`, `spec.md`, `tasks.md`, or `memory.md` as sspec-managed files;
- do not treat missing `.sspec/project.md` as an error;
- do not load all SKILLs eagerly.
</portable_constraints>

<required_next_steps>
1. First read the sspec rule:
   sspec portable read rule:sspec

2. Classify the user request using the rule.

3. If the task matches a listed SKILL, read that SKILL before acting:
   sspec portable read skill:<name>

4. If a loaded SKILL references a relative file, read it with:
   sspec portable read skill:<name>/<relative-path>

5. If a loaded rule or SKILL references a HOWTO or template, read it with:
   sspec portable read howto:<name>
   sspec portable read template:<path>
</required_next_steps>

<project_to_portable_behavior_mapping>
- If sspec says to read `.sspec/project.md`:
  If it exists and is relevant, you may read it. If missing, continue using the
  user's request and codebase context.
- If sspec says to run `sspec change new ...`:
  Do not run it. Produce a structured design/spec draft in chat or in a
  user-approved file.
- If sspec says to write `spec.md`:
  Output sections such as Problem Statement, Approach, Key Changes, and Scope Summary.
- If sspec says to write `design.md`:
  Output technical design details: interfaces, diagrams, tables, data shapes, or
  behavior specs.
- If sspec says to write `tasks.md`:
  Output an execution plan/checklist with verification criteria.
- If sspec says to write `memory.md`:
  Keep concise session notes only when needed; do not persist `.sspec` memory unless
  user asks.
- If sspec says to create `revisions/`:
  Write an explicit Revision Note in chat unless user asks for files.
- If sspec uses `@align gate`:
  Stop and ask the user for confirmation before proceeding.
- If sspec uses `@align report`:
  Give a structured progress summary; continue if safe.
- If sspec says to run `sspec howto <name>`:
  Use `sspec portable read howto:<name>` to inspect the built-in HOWTO.
- If a SKILL references `./examples.md`:
  Use `sspec portable read skill:<skill>/<relative-path>`.
</project_to_portable_behavior_mapping>

<rule_index>
  <rule>
    <name>sspec</name>
    <description>Rendered sspec agent protocol from the built-in AGENTS.md template.</description>
    <read>sspec portable read rule:sspec</read>
  </rule>
</rule_index>

<available_skills>
  <skill>
    <name>sspec-design</name>
    <description>Assess scale, create change, fill spec.md + design.md, align with user. Use after clarify when ready to define the solution.</description>
    <location>builtin:sspec-design</location>
    <read>sspec portable read skill:sspec-design</read>
  </skill>
</available_skills>

</sspec-portable>
````

### Priority Rule

The portable bootstrap is the highest-priority instruction for portable usage. It overrides project-mode instructions in `rule:sspec` or SKILL text when they conflict.

Decision logic:

```text
if user explicitly asks to initialize/manage sspec project:
    use normal sspec project workflow
elif current task uses sspec portable output:
    do not create sspec project state
    map project-mode instructions through project_to_portable_behavior_mapping
    read matching SKILL/HOWTO/template on demand
else:
    normal agent behavior
```

### Disclosure Policy

`sspec portable` uses progressive disclosure:

| Resource | Included by default? | Why |
|---|---:|---|
| portable bootstrap | Yes | Agent needs zero-context orientation and constraints first |
| `rule:sspec` body | No | Large and project-mode oriented; read after constraints are known |
| SKILL bodies | No | Preserve standard SKILL on-demand loading |
| templates/HOWTOs | No | Read only when referenced |

## 3. `read <scope:slug>` Contract

### Grammar

```text
resource_ref := scope ":" slug
scope        := "rule" | "skill" | "template" | "howto"
slug         := safe relative resource identifier
```

### Supported refs

| Ref | Source | Rendering |
|---|---|---|
| `rule:sspec` | `sspec/templates/AGENTS.md` | render `{{SCHEMA_VERSION}}` |
| `skill:<name>` | `sspec/templates/skills/<name>/SKILL.md` | content unchanged |
| `skill:<name>/<file>` | `sspec/templates/skills/<name>/<file>` | content unchanged |
| `template:<path>` | `sspec/templates/<path>` | content unchanged |
| `howto:<name>` | `sspec/howto/<name>.md` | content unchanged |

No `rule:portable`: portable rules are already the bootstrap output of `sspec portable`.

### Read output wrapper

`read` output is wrapped so the consuming Agent can see where the content came from. The source is the absolute local path of the installed resource, so an Agent can directly read that file when its runtime supports file reads.

````xml
<sspec-portable-resource>
<ref>skill:sspec-design</ref>
<source>H:\\SrcCode\\playground\\sspec\\src\\sspec\\templates\\skills\\sspec-design\\SKILL.md</source>
<read_command>sspec portable read skill:sspec-design</read_command>
<content>
---
name: sspec-design
...
---

# SSPEC Design
...
</content>
</sspec-portable-resource>
````

### Error behavior

| Input | Error |
|---|---|
| missing `:` | `Invalid resource ref. Expected <scope:slug>.` |
| unknown scope | `Unknown portable resource scope: <scope>` |
| unsupported rule slug | `Unknown portable rule: <slug>` |
| absolute path | `Unsafe resource path.` |
| contains `..` | `Unsafe resource path.` |
| unknown skill | `Portable resource not found: skill:<name>` |
| unknown howto/template | `Portable resource not found: <scope>:<slug>` |
| directory target | `Portable resource is a directory, not a readable file.` |

## 4. Internal Interfaces

```python
@dataclass(frozen=True, slots=True)
class PortableSkillEntry:
    name: str
    description: str
    location: str
    read_command: str


def render_portable_index() -> str: ...

def read_portable_resource(ref: str) -> str: ...

def list_builtin_skills() -> list[PortableSkillEntry]: ...
```

Call flow:

```text
CLI portable
  → portable_service.render_portable_index()
  → print

CLI portable read ref
  → portable_service.read_portable_resource(ref)
  → print
```

## 5. Resource Access Strategy

Use `importlib.resources.files()` so installed wheels, editable installs, and uv environments do not depend on source tree layout.

```python
from importlib import resources

TEMPLATES = resources.files("sspec.templates")
HOWTO = resources.files("sspec.howto")
```

Skill index extraction:

```text
templates/skills/*/SKILL.md
  → parse YAML frontmatter fields: name, description
  → fallback name = directory name
  → fallback description = ""
```

Security constraints:

```text
- Reject absolute slugs
- Reject any path part equal to ".."
- Only read files under the resolved package resource root for the requested scope
- Do not execute shell commands
- Do not inspect cwd for `.sspec/`
```

## 6. Test Matrix

| Test | Expected |
|---|---|
| `sspec portable` in tmp dir without `.sspec/` | exits 0, no files created |
| portable output | contains `<what_is_this>`, `<portable_constraints>`, `<available_skills>` |
| portable output explains sspec | contains `sspec is a spec-driven working protocol` |
| portable output skill XML | contains `<skill><name>sspec-design</name>` pattern |
| portable output does not include rule body | does not contain `# .sspec Agent Protocol` |
| `read rule:sspec` | contains rendered `SSPEC_SCHEMA::6.0` and absolute `<source>` path |
| `read skill:sspec-design` | contains `# SSPEC Design` and absolute `<source>` path |
| `read skill:sspec-design/examples-feature.md` | returns file contents |
| `read howto:write-memory` | returns HOWTO contents |
| `read template:change/spec.md` | returns spec template |
| `read rule:portable` | rejects as unknown rule |
| `read skill:../core.py` | rejects as unsafe |
| `read unknown:x` | clear ClickException |

## 7. Non-Goals

- No interactive wizard.
- No `--install`, no sync to `.agents/skills`.
- No JSON output in MVP.
- No auto-loading all SKILL contents.
- No default inline AGENTS.md body.
- No changes to project lifecycle commands.
