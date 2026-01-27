---
status: PLANNING
type: ""
created: {{TIME}}
---

# {{CHANGE_NAME}}

<!-- @AGENT: READ THIS CAREFULLY
SSPEC Change Lifecycle:
  PLANNING → DOING → REVIEW → DONE (or BLOCKED at any point)

Document Responsibilities:
- spec.md = WHY/WHAT (problem, solution, design decisions)
- tasks.md = HOW (executable tasks <2h each)
- handover.md = CONTINUITY (session bridge—update EVERY session end)

For detailed guidance, consult sspec SKILL.

Optional Auxiliary Files:
- reference/ — detailed design docs, research notes, drafts
- scripts/ — migration scripts, test data, utilities
-->

## A. Proposal and Problem Statement

### Current Situation

<!-- @AGENT: Describe current pain points. Quantify when possible:
- Performance: response time, throughput
- Quality: bug rate, user complaints
- Efficiency: dev time, repetitive work
-->

### User Request / Requirement

<!-- @AGENT: What does the user want to achieve?
- Specific feature requirements
- Expected improvement metrics
- Acceptance criteria
-->

## B. Proposed Solution

### Framework of Idea

<!-- @AGENT: Core approach (1-3 paragraphs):
- What solution are we adopting?
- Why this solution over alternatives?
- Trade-offs and comparisons (if any)
-->

### Key Changes

<!-- @AGENT: List key changes:
1. New/modified core modules
2. Interface/data structure changes
3. Dependency/configuration changes
-->

## C. Implementation Strategy

<!-- @AGENT: ⚠️ CRITICAL: Break down to FILE LEVEL

Format:
### Phase N: <Phase Name>
- `path/to/file.py` — <create|modify>, <change description>
- `path/to/another.py` — <create|modify>, <change description>

Example:
### Phase 1: Infrastructure
- `src/cache/redis.py` — create, Redis connection pool
- `src/config/settings.py` — modify, add Redis config
- `requirements.txt` — modify, add redis dependency

### Phase 2: Core Logic
- `src/auth/middleware.py` — modify, cache-first validation
- `tests/test_auth.py` — modify, add cache tests

### Risks & Dependencies
- <External dependencies>
- <Potential risks and mitigation>

Optional: If complex, create reference/design.md for detailed design
## D. Blockers & Feedback

<!-- @AGENT: Document blockers and user feedback

### Blocker (YYYY-MM-DD)
**Blocked**: <What is blocked>
**Impact**: <Impact on progress>
**Needed**: <Info/resources needed to unblock>

### Feedback (YYYY-MM-DD)
<User feedback and how it's addressed>

### PIVOT (YYYY-MM-DD)
<If major direction change, record reason and new direction>
-->
