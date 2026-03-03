---
name: analyse-project-level
created: 2026-03-02 22:43:42
status: DOING
attach-change: .sspec/changes/26-03-03T00-46_analyse-project-level/spec.md
tldr: ''
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: analyse-project-level

## Problem
<!-- What is not working or missing -->

1. 请分析 .meta.json 文件的机制 —— 这个文件是很久很久之前设计的，迭代到现在我不确定有没有相关的 BUG 或者不良设计
2. 初始化的时候 (project init) 允许选择 .claude, .copilot, .agnet，我需要
   1. 把 .agent 改为 .agents
   2. 允许增加额外选项，让用户自己输入文件目录
3. 当前有个问题，项目初始化之后，似乎没有办法再增加新的 SKILL 绑定文件夹？SKILL 命令中似乎不会更新 .meta.json 吧？请分析这个问题。
4. 当前 .meta.json 中的 schema_version 其实是有问题的，是直接复用了 AGENTS.md 的 schema，而非 meta.json 本身的 schema；这回导致后面如果要更新 meta.json 的结构会很难。
5. 请分析目前 .sspec 创建是默认的 gitignore 方案是否合理。

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

请综合调研这些问题，并给出你的想法和方案。

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.

---

<!-- ============================================================
     MICRO-CHANGE ZONE (optional)
     For tiny changes (≤3 files, ≤30min) that don't need a full change.
     Remove these sections if a change is created instead.
     ============================================================ -->

<!--
## Plan
Quick implementation plan (what files to touch, what to do)

## Done
What was actually done + any notes for future reference
-->
