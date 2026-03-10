---
name: read-long-mdfile
desc: Use `sspec tool mdtoc` before reading long markdown files.
---

When a Markdown file is long, do not read it blindly from line 1.

- Default sequence: run `sspec tool mdtoc <file-pattern>` -> inspect size and heading tree -> pick the exact section -> read only that range -> expand only if needed.
- Use this by default for long SKILL files, `AGENTS.md`, spec-docs, and large request / change files.
- Pay attention to total lines / chars, the main heading tree, where the relevant section starts, and where the next heading starts.
- `mdtoc` can handle multiple files by input with dir or globs.

Rule of thumb: if you hesitate before reading the whole file, run `mdtoc` first.
