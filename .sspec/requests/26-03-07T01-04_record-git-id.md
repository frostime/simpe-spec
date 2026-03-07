---
name: record-git-id
created: 2026-03-07 01:04:11
status: DONE
attach-change: .sspec/changes/26-03-07T01-48_record-git-id/spec.md
tldr: 'Capture pre-creation Git baseline into change handover templates so agents can see the true starting branch, HEAD, and status.'
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: record-git-id

## Problem
<!-- What is not working or missing -->
我在使用 Agentic Code 的时候，总是配合 GIT 使用
Agent 也经常需要比对 git log ； 我也推荐 Agent 经常使用 git diff 做审查。

常见的模式有两种：
- 每次 confirm 了内容之后，就 git add; 等到全部完成之后，git commit
- 开一个独立的 branch, 每次 confirm 之后就 git commit -m "wip: xxx"；全部弄完之后，就 squash merge

所以我在思考：在 change 的默认模板中增加一个 {{GIT}} 的占位符，记录创建 change 时候的 git 信息是否会很有帮助呢?

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->
有几个要点

**存在哪里?**
有两个选项：
- 放在 handover.md 中
- 放在 spec.md 中

**不准更新**: 这个 GIT 是记录 change 起点位置的，所以只能在创建模板的时候自动渲染，不能允许Agent更新

**填入什么?**
必要的: 创建 change **之前** git 状态，branch commit hash 等
特别注意要在创建之前计算，不然创建 change 本身会改变 git status

疑惑：如果当前 git 并非干净，例如存在 modified, staged 的要怎么办?


## Success Criteria
<!-- The conditions or criteria that indicate
the problem has been resolved and meets the user's intention -->
对于 Agent 来说他能非常正确的理解当前 change 在 git graph 中所在的状态

## Relational Context
<!-- Constraints, preferences, related filelinks -->

- src\sspec\templates\change
- src\sspec\templates\change-root
- src\sspec\services\change_service.py
- src\sspec\core.py - copy_template

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.

Note: @force-end-align, 使用内置的 question 工具
