---
name: update-readme
description: Automate README updates and i18n translations. Use when project features change and documentation needs sync.
metadata:
  author: frsotime
  version: 1.0.0
---

# Update README Skill

**When to use**:
- After implementing new features
- After modifying AGENTS.md or SKILLs
- Before release/version bump
- When user asks to update documentation

---

## Workflow

```
Step 1: DETECT CHANGES
├─ Run: git status
├─ Run: git diff --name-only HEAD~5  (or appropriate range)
├─ Identify: Which features/SKILLs/CLI commands changed?
└─ Note: Files affecting README (AGENTS.md, CLI, templates)

Step 2: READ CURRENT STATE
├─ Read: README.md (English source)
├─ Read: README_zh-CN.md (Chinese translation)
├─ Read: i18n-glossary.md (terminology reference)
└─ Identify: Sections needing update

Step 3: UPDATE ENGLISH README
├─ Apply changes per detected diffs
├─ Follow Writing Style Guidelines (below)
├─ Ensure CLI examples are accurate
└─ Verify file structure diagrams match reality

Step 4: TRANSLATE TO CHINESE
├─ Reference: i18n-glossary.md for consistent terms
├─ Translate: Section by section
├─ Preserve: Code blocks, file paths, command syntax
└─ Adapt: Phrasing for natural Chinese (not word-by-word)

Step 5: VERIFY
├─ All CLI commands exist and work
├─ File paths in examples are valid
├─ No orphaned sections between languages
└─ Glossary terms used consistently
```

---

## Writing Style Guidelines

### Tone

| ✅ Do | ❌ Don't |
|-------|---------|
| Direct, factual statements | Marketing speak ("revolutionary", "powerful") |
| Specific metrics ("30 seconds") | Vague claims ("fast", "efficient") |
| Show, don't tell (examples) | Abstract descriptions |
| Problem → Solution structure | Feature lists without context |

### Structure

```markdown
## Section Name

[1-2 sentence description of what this does]

[Code example or command]

[Brief explanation if needed]
```

### Code Examples

- **Real commands**: Must actually work
- **Realistic names**: `add-auth`, `payment-system` (not `foo`, `example`)
- **Show output**: When output clarifies behavior
- **Minimal**: Shortest example that demonstrates the point

### Language

| Pattern | ❌ Avoid | ✅ Use |
|---------|---------|--------|
| Hedging | "You might want to..." | "Run X to do Y" |
| Passive | "Changes are tracked by..." | "sspec tracks changes in..." |
| Filler | "It's worth noting that..." | (just state the fact) |
| Jargon | "Leverage the paradigm" | "Use the workflow" |

### Section Checklist

For each README section, verify:
- [ ] States what it does (not why it's great)
- [ ] Includes working example if applicable
- [ ] Links to details if too long for README
- [ ] Consistent with AGENTS.md terminology

---

## i18n Translation Rules

### Must Translate
- Descriptions and explanations
- Section headings
- Comments in code blocks

### Must NOT Translate
- Command names: `sspec`, `git`
- File names: `spec.md`, `handover.md`
- Directory paths: `.sspec/changes/`
- Status values: `PLANNING`, `DOING`
- Code syntax
- CLI flags: `--name`, `--dir`

### Glossary Enforcement

Before translating, load `i18n-glossary.md` and:
1. Search for all English terms in glossary
2. Replace with designated Chinese terms
3. Verify no inconsistent translations

Example:
```
English: "Create a new change"
Glossary: Change → 变更
Chinese: "创建新变更"

NOT: "创建新更改" (wrong term)
```

### Natural Adaptation

Don't translate word-by-word. Adapt for natural Chinese:

| English | Literal (❌) | Natural (✅) |
|---------|-------------|--------------|
| "AI reads handover.md and picks up where you left off" | "AI 读取 handover.md 并从你离开的地方继续" | "AI 读取 handover.md，从上次中断处继续" |
| "Tell your AI to..." | "告诉你的 AI 去..." | "让 AI 执行..." |

---

## Update Checklist

### Before Starting
- [ ] `git status` shows relevant changes
- [ ] Understand what features changed
- [ ] Have access to i18n-glossary.md

### English README
- [ ] Feature descriptions match implementation
- [ ] CLI commands are accurate
- [ ] File structure diagram is current
- [ ] Examples use realistic names
- [ ] No marketing language

### Chinese README
- [ ] All sections translated
- [ ] Glossary terms used consistently
- [ ] Code blocks preserved exactly
- [ ] Natural Chinese phrasing
- [ ] Language switcher link works

### Final Verification
- [ ] Both READMEs have same sections
- [ ] Version/date updated if applicable
- [ ] No broken internal links

---

## Common Updates

### New CLI Command

1. Add to CLI Reference table (both languages)
2. Add usage example if non-obvious
3. Update "Quick Start" if it's a common command

### New Concept (e.g., sspec ask)

1. Add to relevant workflow section
2. Add to glossary if new term
3. Translate term, add to i18n-glossary.md
4. Update file structure if new directory

### Changed Workflow

1. Update workflow section
2. Verify AGENTS.md consistency
3. Update diagrams if flow changed
4. Check examples still valid

---

## Automation Commands

```bash
# Check what changed
git diff --name-only HEAD~5 | grep -E "(README|AGENTS|SKILL|cli)"

# Verify CLI commands work
sspec --help
sspec project --help
sspec change --help

# Check file structure matches docs
ls -la .sspec/
```

