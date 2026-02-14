---
name: SKILL Installation & Sync
description: sspec 中 SKILL 的安装、同步、更新与 legacy 迁移设计
updated: 2026-02-13
scope:
  - /src/sspec/skill_installer.py
  - /src/sspec/services/project_init_service.py
  - /src/sspec/services/project_update_service.py
  - /src/sspec/commands/project.py
  - /tests/test_skill_installer.py
  - /tests/test_project_init_service.py
  - /tests/test_project_init_skill_sync.py
  - /tests/test_project_update_service.py
deprecated: false
replacement: ""
---

# SKILL Installation & Sync

## Overview
本规范定义 `sspec` 当前 SKILL 安装体系：以 `.sspec/skills` 为唯一 hub，外部位置（`.agent/.claude/.github`）作为 spoke 同步。

目标：
- 保持 init/update 的行为一致和可回归；
- 在 Windows 上优先链接并兼顾无管理员权限场景；
- 支持从旧版逐 skill 链接布局平滑迁移。

## Current Architecture

```mermaid
graph TD
    T[src/sspec/templates/skills] --> H[.sspec/skills]
    H --> A[.agent/skills]
    H --> C[.claude/skills]
    H --> G[.github/skills]
```

- Hub：`.sspec/skills`（托管技能真源）
- Spoke：外部 agent 目录下的 `skills`（目录级 link 或 copy）

## Init Flow

1. `project init` 先完成 `.sspec` 核心初始化并安装 hub skills。
2. 再询问外部同步位置。
3. Windows 额外询问是否提权创建 symlink：
   - 同意：`symlink -> elevated symlink -> junction -> copy`
   - 不同意：`junction -> copy`
4. 若用户未选择任何外部目录，强制回退 `.agent`，并提示后续可迁移。

## Update Flow

`project update` 执行顺序：
1. legacy layout 迁移（旧版逐 skill 子链接）
2. orphan skill 清理
3. template + skill 更新候选计算
4. 根据状态和 force 策略执行

Skill 候选状态语义（copy 目录）：
- `current`: `current_hash == new_hash`
- `updatable`: `current_hash == old_hash`
- `modified`: 既不等于 `new_hash` 也不等于 `old_hash`
- `unknown`: 缺失 `old_hash` 且不等于 `new_hash`

## Link Detection Contract

`check_path_link(path, expected_target?)` 是 link 判定统一入口：
- 支持 symlink 与 junction
- 不允许业务逻辑直接依赖 `Path.is_symlink()` 判定完整语义

## Gitignore Contract

自动管理通过 fenced block 写入：
- `# >>> sspec-managed skills >>>`
- `# <<< sspec-managed skills <<<`

规则：
- spoke 场景写入父目录（例如 `.github/.gitignore`）并维护 `skills` 条目
- 幂等更新，不重复追加

## Legacy Design (Previous Scheme)

旧方案特征：
- 外部位置采用“逐 skill 子目录链接”
- 更新逻辑按 per-skill copy 候选推断，语义分散
- 在 very-legacy 场景中可能出现首轮仅清理 orphan，次轮才迁移

已改进：
- 迁移条件改为“只要检测到任一指向 hub 的 legacy 子链接即迁移”
- 备份阶段不再重建 symlink（避免 WinError 1314）

## Migration & Rollback Notes

迁移会在 `.sspec/tmp/skills-backup/<timestamp>/` 写入备份。

若迁移后需要回滚：
1. 删除当前 spoke `skills` 路径
2. 从对应 backup 目录恢复
3. 再次运行 `sspec project update`（可配合 `--dry-run` 先检查）

## Decision Notes

- 目录级 spoke 优于逐 skill spoke：结构更稳定，识别更一致。
- Junction 是 Windows 下可接受回退，不与 symlink 判定混用。
- 修改保护优先：`modified` 状态默认不覆盖，需 `--force`。
