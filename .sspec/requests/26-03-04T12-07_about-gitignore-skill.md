---
name: about-gitignore-skill
created: 2026-03-04T12:07:27
status: DONE
attach-change: null
tldr: "Allow tracking custom skills by stopping blanket ignore of `.sspec/skills`, and manage ignore via fenced managed-skill list synced by `project update`."
---

<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: about-gitignore-skill

## Problem
<!-- What is not working or missing -->
我想和你探讨一下 SKILL Ignore 的问题；你可以先查询代码中对 skills 目录的 ignore 设计方案
当前的设计方案是
- .sspec 下忽略 skills
- .sspec/skills 下忽略所有相关的 skill —— 这个是很久之前的惨老
- 其他的 Spoke 目录，比如 .claude 中直接忽略 skills —— 这是为了避免和 .sspec 中的重复

不过这种方案显然有问题，用户想要自行添加的 SKILL 就不会被纳入 git track 当中
之前采用这种方式是因为，sspec 的 skill 可能会随着 Project update 更新，就没有必要 track
不过考虑到上面这种问题，请问我们应该如何解决呢？

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

- 一种方案是直接放开 .sspec/skill 的跟踪
- 第二种是，只 ignore 在 .meta.json 中生命 managed 的 skill
  - 如果是这种，有必要在 gitignore 中声明 block 方便替换更新
  # >>> sspec-managed skills >>>
  xxx
  # <<< sspec-managed skills <<<
  ```

## Relational Context
<!-- Constraints, preferences, related filelinks -->

src\sspec\services\project_init_service.py

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs.

我个人认为这是一个 micro change，可以不用创建 sspec change

---

<!-- ============================================================
     MICRO-CHANGE ZONE (optional)
     For tiny changes (≤3 files, ≤30min) that don't need a full change.
     Remove these sections if a change is created instead.
     ============================================================ -->


## Plan
Quick implementation plan (what files to touch, what to do)

- Update init default `.sspec/.gitignore` to stop ignoring `skills/**`.
- Keep spoke locations ignored (they are links only; `.sspec` is the single source of truth).
- Add `project update` migration:
  - Rewrite `.sspec/skills/.gitignore` fenced block to match current template managed skills.
- Add/adjust tests for init + gitignore fence behavior.

## Done
What was actually done + any notes for future reference

- Implemented the new gitignore model:
  - `src/sspec/services/project_init_service.py` no longer writes `skills/**` into `.sspec/.gitignore` for newly initialized projects.
  - `project update` now:
    - Syncs `.sspec/skills/.gitignore` fenced block to ignore exactly the current managed template skills.
    - Does not mutate `.sspec/.gitignore` (user-owned file, no migration).
  - Spoke locations remain link-only and are ignored at the directory level (`skills`) via the existing fenced block behavior.

- Code refs:
  - `src/sspec/services/project_init_service.py`
  - `src/sspec/services/project_update_service.py`
  - `src/sspec/commands/project.py`
  - `src/sspec/skill_installer.py`

- Tests:
  - Updated `tests/test_project_init_service.py`
  - Added coverage in `tests/test_skill_installer.py`
  - Verified `tests/test_project_init_skill_sync.py`
