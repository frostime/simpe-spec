---
name: make-subagent-audit
desc: Run independent reviews with subagents against a git diff range.
---

Conduct independent code-level reviews using Subagents.

1. Determine the start and end points of the changes at the git level, typically a commit range or `staged` changes.
2. Initiate one or more Subagents and provide them with:
   1. The task requirements and constraints for the changes, optionally including relevant request and change links.
   2. The specified `git diff` command to run, such as `git diff --staged` or `git diff <commit1> <commit2>`.
   3. The focus areas for the code review, such as security, performance, readability, etc.
3. Each Subagent performs the code review based on the provided git diff and focus areas, and outputs review results, which may include:
   1. Identified potential issues and their risk levels.
   2. Suggested improvements and best practices.
4. The main Agent objectively evaluates the Subagent review results, makes decisions in combination with the code files, and ultimately consolidates them into a comprehensive review report.

**Multi-Subagent Division**
When the codebase is complex, multiple Subagents can be employed, for example:
- Multi-Subagents to focus on distinct review dimensions to achieve cross-validation from multiple sources.
- Multi-Subagents to review different code modules, enabling a divide-and-conquer approach to save context overhead.
- Multi-Subagents to conduct independent reviews, ensuring comprehensive coverage and trading computational resources for high-confidence outcomes.

