---
name: sspec-mdtoc
description: "Pre-scan Markdown files before reading. Use `sspec tool mdtoc` to get file size + heading structure with line numbers (L<n> format) before reading long docs, SKILLs, or spec-docs. Eliminates blind reads."
---

# sspec-mdtoc — Markdown Pre-scan Skill

## When to Use

Before reading ANY Markdown file you haven't seen before:
- Long spec-docs, SKILL files etc.
- README or documentation files
- Any `.md` you need to understand structurally first

**Rule**: If you'd read a file top-to-bottom without knowing its size, run mdtoc first.

## Command

```
sspec tool mdtoc <source> [--depth N]
```

| Source Type | Example | Behavior |
|-------------|---------|----------|
| File path | `sspec tool mdtoc README.md` | Analyzes single file |
| Directory | `sspec tool mdtoc docs/` | Globs all `*.md` recursively |
| Glob | `sspec tool mdtoc "**/*.md"` | Matches pattern |
| Default | `sspec tool mdtoc` | Current directory |

`--depth N`: Limit heading depth (1-6, default: 6)

## Output Format

```
=== path/to/file.md ===
chars: 4,523 | lines: 120

L1     # Document Title
L5       ## Section One
L12      ## Section Two
L18        ### Subsection A
L25        ### Subsection B
L30      ## Section Three
```

- `L<n>` — 1-based line number of the heading
- Indent reflects heading hierarchy
- `chars` and `lines` tell you how large the file is before you read it

## Typical Workflow

```
1. sspec tool mdtoc <file>     # Get outline + line ranges
2. Identify sections of interest
3. read_file(startLine=<Ln>, endLine=<next_Ln>)  # Targeted read
```

**Multi-file summary** is shown automatically when scanning a directory:
```
Found 8 files | total chars: 42,310 | total lines: 1,205 | headings: 87
```

## Example: Analyzing a SKILL before reading

```bash
# Instead of blindly reading the entire skill:
sspec tool mdtoc .sspec/skills/sspec-design/SKILL.md

# Output shows sections with line numbers:
# L1   # SSPEC Design
# L8     ## Workflow
# L16    ## Step 1: Assess Scale
# ...

# Now read only the section you need:
# read_file(startLine=16, endLine=30)
```

## Full Specification

To get the complete LLM-optimized specification:
```
sspec tool mdtoc --prompt
```
