---
name: analyse-project-level
status: REVIEW
type: ''
change-type: single
created: 2026-03-03 00:46:34
reference:
- source: .sspec/requests/26-03-02T22-43_analyse-project-level.md
  type: request
  note: Linked from request
---

# analyse-project-level

## A. Problem Statement

调研 `.meta.json` 机制及相关联的初始化、SKILL 管理流程，发现以下 5 个问题：

### 问题 A1 — `.meta.json` 机制中的 Bug 与不良设计

**Bug**: `create_skill_in_hub()` 中 `meta['updated_at'] = __version__`，误把版本号字符串写入了时间戳字段（应为 `datetime.now().isoformat()`）。

**不良设计（无 schema 迁移）**: `load_meta()` 在读取旧版 `.meta.json` 时，若字段缺失直接返回空 dict，调用方需自行用 `.get()` 防御；没有统一的 migration/defaults 机制，随着 meta 结构演进风险增大。

### 问题 A2 — `project init` 中 `.agent` → `.agents`，及不支持自定义目录

- `core.py:WORKSPACE_DIRS = ['.github', '.claude', '.agent']`，实际上正确的目录名是 `.agents`（多数 AI Agent 框架使用）。
- `project.py:_interactive_skill_selection()` 的 `available_locations` 列表 hardcode 为 `['.claude', '.github', '.agent']`，fallback 到 `.agent`；CLI `--skill-loc` choice 也仅限三个固定值。
- 无法输入自定义目录（如 `.windsurf`, `.cursor`, `.myagent` 等）。

### 问题 A3 — `skill dominate` 不更新 `.meta.json`

`skill dominate <dir>` 将目标目录的 `skills/` 链接到 `.sspec/skills/`，但 **不写入** `meta['skill_locations']`。后续 `project update` 依赖 `skill_locations` 同步 spoke，导致通过 `dominate` 新增的位置在 update 时被遗漏，无法享受自动更新。

### 问题 A4 — `.meta.json` 中 `schema_version` 复用 AGENTS.md 的 schema

`SCHEMA_VERSION = '9.1'` 是 AGENTS.md 协议版本，非 `.meta.json` 自身结构版本。两者粒度和更新频率不同，复用导致：
- 无法独立演进 meta.json 字段结构；
- 未来若需加新字段并迁移旧 meta.json，缺乏可靠版本基准。

### 问题 A5 — `.sspec/.gitignore` 设计不合理

当前 `DEFAULT_GITIGNORE`：
```
!project.md
!spec-docs/**
!commands/**
!.meta.json
changes/**
requests/**
skills/**
asks/**
tmp/**
```

问题：
1. **`!` 规则无效**：没有前置 `*` 通配符，`!project.md` 等否定规则对未被忽略的文件不起作用，是纯粹的冗余噪声。
2. **`changes/**` 和 `requests/**` 被忽略不合理**：这些是重要的协作上下文（spec.md、tasks.md、handover.md），应当提交到 git。
3. **`asks/**` 被忽略可能不合理**：asks 是决策记录，类似 requests，应提交。
4. **`!commands/**` 是幽灵规则**：`.sspec/` 下根本不存在 `commands/` 目录。

---

## B. Proposed Solution

### Fix A1 — 修复 `updated_at` Bug + 增加 meta defaults helper

**Fix A1a（Bug）**: 在 `skill_service.py:create_skill_in_hub()` 中，将 `meta['updated_at'] = __version__` 改为 `meta['updated_at'] = datetime.now().isoformat()`。

**Fix A1b（defaults + typed model + migrations）**: 在 `meta_service.py` 中建立明确的 meta 数据模型，并实现基于 schema 的迁移策略。

核心原则：
- `.meta.json` 是版本化配置文件，必须有独立 schema 标识 `meta_schema`。
- `meta_schema`（meta 文件 schema）与 `sspec_schema`（AGENTS.md 协议 schema）是两条独立版本轴。
- `load_meta` 对调用方提供稳定键（通过迁移），但在文件缺失/损坏时返回 `{}`。

迁移实现：
- 当前 `meta_schema` 定义为 `2.0`
- schema 驱动升级：`0.0 -> 1.0 -> 2.0`（缺失 schema 视为 `0.0`）
- 2.0 的关键变更：
  - `schema_version` -> `sspec_schema`
  - `meta_schema_version` -> `meta_schema`

（实现细节见：`src/sspec/services/meta_service.py`）

### Fix A2 — 重命名 `.agent` → `.agents`，增加自定义目录输入

**Fix A2a**: 在 `core.py` 中将 `WORKSPACE_DIRS` 的 `'.agent'` 改为 `'.agents'`，CLI choice list 和 fallback 同步更新。

**Fix A2b**: 在 `_interactive_skill_selection()` 的 checkbox 列表末尾增加一个 "Enter custom path…" 选项，用户选择后触发 `questionary.text()` 输入；或在 checkbox 结束后追问自定义路径。

**Fix A2c**: CLI `--skill-loc` 选项改为 `type=str`（不限 choice），但在 `sync_skill_locations` 入口做路径合法性校验。

### Fix A3 — `skill dominate` 写入 `.meta.json`

在 `skill.py:dominate` 命令末尾（成功后），调用已有的 `sync_skill_locations` 或直接更新 meta：

```python
# After successful dominate:
meta = load_meta(sspec_root)
stored = set(meta.get('skill_locations', []))
stored.add(dominate_dir.relative_to(project_root).as_posix() + '/skills')
meta['skill_locations'] = sorted(stored)
save_meta(sspec_root, meta)
```

或者将此逻辑封装到 `dominate_skills_location` 服务内（接受 `project_root` 参数）。

### Fix A4 — meta_schema v2 + 迁移与 update 集成

引入 `meta_schema` 作为 `.meta.json` 的独立 schema 标识（当前为 `2.0`），并将 meta 迁移变成 `project update` 的必经环节：

- `project init` 写入：`meta_schema` 与 `sspec_schema`
- `project update` 第一阶段执行 meta 加载+迁移+校验（失败则 CLI 友好报错）
- 即使没有任何文件需要更新，只要 meta 需要迁移，也必须写回最新 schema

（实现细节见：`src/sspec/services/project_update_service.py` 与 `src/sspec/commands/project.py`）

### Fix A5 — 修复 `.gitignore` 方案

新的 `DEFAULT_GITIGNORE`：

```
# sspec working data - commit project context, ignore generated/temp files
changes/**
requests/**
asks/**
skills/**
tmp/**

# Keep important project context
!changes/
!requests/
!asks/
```

**策略调整**：
- 去掉 `!project.md` 等无效否定规则（`.meta.json`、`project.md`、`spec-docs/` 都不在任何忽略规则下，无需否定）。
- `changes/**` + `!changes/` 模式：忽略 changes 下的文件，但保留目录本身（git 不追踪空目录，这个组合实际意味着 changes/ 目录本身会被追踪，内容被忽略）。
- 实际上更合理的方案是：**`changes/`、`requests/`、`asks/` 默认提交**（删掉对应的忽略行），只忽略 `skills/**` 和 `tmp/**`。

**Recommended default**（最简洁、最合理）：
```
# Installed skills (managed by sspec, not for VCS)
skills/**
# Temp workspace
tmp/**
```

这样 `changes/`、`requests/`、`asks/`、`project.md`、`spec-docs/`、`.meta.json` 全部默认提交，符合协作目的。`skills/` 忽略因为它是安装产物（symlink 或 copy），`tmp/` 忽略因为是工作区草稿。

---

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/core.py` | Fix A2a: `.agent` → `.agents` in `WORKSPACE_DIRS` |
| `src/sspec/commands/project.py` | Fix A2a/b/c: update skill loc list, add custom input, fallback rename |
| `src/sspec/services/meta_service.py` | Fix A1b/A4: `MetaModel` + schema-based migrations (`meta_schema=2.0`), legacy key rename |
| `src/sspec/services/project_update_service.py` | Fix A4: `prepare_meta_for_project_update()` mandatory migration stage |
| `src/sspec/services/project_init_service.py` | Fix A4: write `meta_schema` + `sspec_schema`; Fix A5: new DEFAULT_GITIGNORE |
| `src/sspec/services/skill_service.py` | Fix A1a: fix `updated_at` bug; Fix A3: dominate writes meta |
| `src/sspec/commands/skill.py` | Fix A3 (alt): update meta after dominate if done in command layer |
| `tests/` | Update affected tests |
| `.sspec/spec-docs/meta-json.md` | New spec-doc: `.meta.json` schema + migration + update-time guarantees |
