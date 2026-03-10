---
name: write-howto
desc: Write HOWTO docs as directive, agent-facing operating guides for one concrete job.
---

HOWTO is a micro SKILL/RULE for agent system.
The reader is an AGENT/LLM model; it collects rules by running `sspec howto <name>`.
A HOWTO must be concrete, focused, directive, and actionable without human interpretation.

**Do this**
- Solve one job only. If the draft answers multiple questions, split it.
- Good targets: one document-writing rule, one reading procedure, one alignment pattern, one review / handover action.
- Bad targets: a whole lifecycle, a broad role description, or a mixed style guide.
- Use a verb-led `name`; keep `desc` short.
- Hard limit: about 2K words and 60 lines. Recommended: within 1.5K words and 50 lines.
- If header sections are needed, top level starts at `##`; keep hierarchy shallow.
- Clear action is recommended, like `Read file at xxx`, `Run shell command xxx`.

**Not that**
- Do not copy large background blocks; keep only the part that specific action.
- Avoid wording like "it may help" or "you may want to consider".
