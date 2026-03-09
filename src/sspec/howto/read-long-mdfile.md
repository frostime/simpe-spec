---
name: read-long-mdfile
desc: Use `sspec tool mdtoc` before reading long markdown files.
---

When a Markdown file is long, do not read it blindly.

Use this sequence:
1. Run `sspec tool mdtoc <file>` first.
2. Check file size and heading structure.
3. Jump only to the sections you actually need.
4. Read the relevant ranges instead of the whole file.

Use this especially for:
- long SKILL files
- spec-docs
- large request or change documents
- any markdown with many sections

Reason:
`mdtoc` gives a fast map of the document, which reduces blind reads and keeps context focused.
