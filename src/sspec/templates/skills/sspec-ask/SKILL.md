---
skill: sspec-ask
version: 2.0.0
description: Mid-execution user consultation with persistent Q&A records. Use actively when needing human input.
---

# SSPEC Ask Skill

**When to consult**: First time using `sspec ask`, or need multi-line question syntax.

**Basic rule** (from AGENTS.md): Use when information missing, directional choice needed, completion check, or repeated failures.

---

## Command Syntax

```bash
sspec ask --name "<topic>" --why "<reason>" --question "<question>"
```

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | Yes | Topic identifier (used in filename) |
| `--why` | No (recommended) | Intent for future reference |
| `--question` | Yes | Question text. Use `-` for stdin |

**Output**: User prompted for answer. Record saved to `.sspec/asks/<timestamp>_<name>.md`

---

## Multi-Line Questions

### PowerShell (here-string)

```powershell
sspec ask --name "api_design" --why "Multiple valid approaches" --question @'
Which API style do you prefer?

1) REST with nested resources
   `/users/{id}/orders/{orderId}`

2) Flat endpoints with query params
   `/orders?userId={id}&orderId={orderId}`

Please explain your reasoning.
'@
```

### Bash/Zsh (heredoc)

```bash
sspec ask --name "api_design" --why "Multiple valid approaches" --question - << 'EOF'
Which API style do you prefer?

1) REST with nested resources
   `/users/{id}/orders/{orderId}`

2) Flat endpoints with query params
   `/orders?userId={id}&orderId={orderId}`

Please explain your reasoning.
EOF
```

---

## Use Case Examples

### 1. Missing Information

```bash
sspec ask --name "db_credentials" \
  --why "Cannot proceed without connection info" \
  --question "What are the database connection details? (host, port, user, password)"
```

### 2. Directional Choice

```bash
sspec ask --name "error_handling" \
  --why "Architecture decision needed" \
  --question @'
How should we handle API errors?

A) Return HTTP status codes only (400, 404, 500)
B) Return JSON error objects with codes and messages
C) Both: status codes + JSON body

This affects all endpoint implementations.
'@
```

### 3. Completion Check

```bash
sspec ask --name "feature_complete" \
  --why "Verify before marking REVIEW" \
  --question "I've completed the auth refactor. Please verify: 1) Login works 2) Token refresh works 3) Logout clears session. Ready to mark as REVIEW?"
```

### 4. Repeated Failures

```bash
sspec ask --name "test_failure" \
  --why "Cannot diagnose after 3 attempts" \
  --question @'
`pytest tests/test_auth.py` fails repeatedly with:

ConnectionRefusedError: [Errno 111] Connection refused

I've tried:
1. Checking if Redis is running (it is)
2. Verifying connection string
3. Running with verbose logging

What am I missing?
'@
```

---

## Guidelines

| Do | Don't |
|----|-------|
| Use specific `--name` for searchability | Use generic names like "question1" |
| Include `--why` for future context | Omit why (makes records less useful) |
| Ask one focused question | Bundle multiple unrelated questions |
| Provide options when applicable | Leave question open-ended if choices exist |
| Use markdown formatting in questions | Use headers above H3 (###) |

---

## Record Format

Saved to `.sspec/asks/<yymmddHHMMSS>_<name>.md`:

```markdown
---
name: api_design
why: Multiple valid approaches
timestamp: 2026-01-27T14:30:00
---

## Question

Which API style do you prefer?
...

## Answer

Option B - JSON error objects. We need structured errors for the mobile app to display localized messages.
```

Records persist for future reference and can be linked from change documents.

