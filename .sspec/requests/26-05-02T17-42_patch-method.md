---
name: patch-method
created: 2026-05-02T17:42:04
status: OPEN
attach-change: null
tldr: ""
---

<!-- MUST follow frontmatter schema:
status: OPEN | DOING | DONE | CLOSED
tldr: One-sentence summary for list views — fill this! -->

# Request: patch-method

## Problem


当前的 builtin tool 中支持 patch tool，非常有用；但是我注意到当前的 Edit 似乎是顺序执行的，这可能带来意外的错误

比如：原文 foo bar, patch : foo -> bar, bar -> tee

结果报错，因为第二条 rule apply 的时候发现了两个 bar.

---

Think: 是不是应该做两阶段，先 match，确认范围，然后 repalce？

Question: 这里就需要考虑 match 之后发现了 overlap scope 怎么办了；一种最简单的策略就是停下来报错

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Approach. -->

请你首先梳理当前的 patch 算法是如何 apply 的，然后讨论优化策略

## Success Criteria
<!-- Conditions that indicate the problem has been resolved and meets the user's intention -->
让 sspec tool patch 正确率更高，让 AGENT 更容易写对 patch blocks

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol and commence development from the current Request file, following the SSPEC Change Lifecycle.
Next step: Read `sspec-clarify` SKILL + `sspec-design` SKILL + `sspec change new --from <this>`.
