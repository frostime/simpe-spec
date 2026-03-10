---
name: use-sspec-ask
desc: Record decisions with `sspec ask` when the answer must survive the current turn.
---

**How to use `sspec ask`**: Treat the flow as one unit: Run `sspec ask create` -> fill `reason` -> fill `question` -> Run `sspec ask prompt <path>`.
**DO NOT** disrupt after `create` command and fill content, the `sspec ask prompt` **MUST** be followed right after the content is filled.

**Notice**
- Ask for one decision or one tightly related bundle; batch only when the same context genuinely belongs together.
- Do not dump long analysis into the question body; link a separate draft instead.
- Do not use `sspec ask` for trivial temporary preferences that a lightweight question tool can handle.
- Do not ask after the risky action already happened.
