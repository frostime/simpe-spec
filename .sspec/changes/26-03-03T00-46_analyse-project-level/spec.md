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

**Fix A1b（defaults）**: 在 `meta_service.py` 中增加 `get_meta_defaults()` 函数，返回 meta 的默认字段结构，供 `load_meta` 在字段缺失时填充（不强制迁移，仅 soft-defaults）：

```python
def get_meta_with_defaults(meta: dict[str, Any]) -> dict[str, Any]:
    """Return meta with missing fields filled by defaults (non-destructive)."""
    defaults = {
        'meta_schema_version': META_SCHEMA_VERSION,
        'schema_version': '',
        'sspec_version': '',
        'created_at': '',
        'updated_at': '',
        'file_hashes': {},
        'managed_skills': [],
        'skill_locations': [],
        'skill_install_strategies': {},
    }
    return {**defaults, **meta}
```

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

### Fix A4 — 引入独立的 `META_SCHEMA_VERSION`

在 `meta_service.py` 中定义：
```python
META_SCHEMA_VERSION = '1'   # 独立版本，从 1 开始
```

`initialize_project` 写 meta 时使用 `meta_schema_version: META_SCHEMA_VERSION`（新字段），保留 `schema_version: SCHEMA_VERSION`（向后兼容，记录 AGENTS.md schema 版本信息，后续可考虑移除）。

`project update` 中可利用 `meta_schema_version` 做未来的结构迁移。

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
| `src/sspec/services/meta_service.py` | Fix A4: add `META_SCHEMA_VERSION`; Fix A1b: add `get_meta_with_defaults()` |
| `src/sspec/services/project_init_service.py` | Fix A4: use `meta_schema_version`; Fix A5: new DEFAULT_GITIGNORE |
| `src/sspec/services/skill_service.py` | Fix A1a: fix `updated_at` bug; Fix A3: dominate writes meta |
| `src/sspec/commands/skill.py` | Fix A3 (alt): update meta after dominate if done in command layer |
| `tests/` | Update affected tests |
