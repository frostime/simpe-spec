---
name: testing-standards
description: "sspec 测试编写规范：分层策略、行为契约、命令层边界与反模式"
updated: 2026-03-07
scope:
  - /tests/**
  - /src/sspec/services/**
  - /src/sspec/libs/**
  - /src/sspec/core.py
  - /src/sspec/skill_installer.py
  - /src/sspec/commands/**
  - /src/sspec/builtin_tools/**
deprecated: false
replacement: ""
---

# Testing Standards

## 0. 核心原则

测试只服务于 **行为契约**。
一个测试必须回答明确问题：当输入、磁盘状态、命令参数满足某个条件时，系统是否产生了约定结果。

删掉一个测试后，如果不会失去任何缺陷探测能力，这个测试就是噪声。

---

## 1. 分层测试策略

sspec 当前代码层次与推荐测试方式如下：

| 层级 | 位置 | 主要策略 |
|------|------|----------|
| 纯工具 | `src/sspec/libs/` | 单元测试，尽量无 I/O |
| 共享核心 | `src/sspec/core.py` | 单元测试 + 少量文件系统验证 |
| 安装/链接 | `src/sspec/skill_installer.py` | 以 `tmp_path` 为核心的行为测试，必要时隔离子进程 |
| 业务逻辑 | `src/sspec/services/` | 文件系统集成测试（`tmp_path` / 临时项目骨架） |
| 命令层 | `src/sspec/commands/` | 选择性 `CliRunner`/错误处理测试，不测富文本样式 |
| 内建工具 | `src/sspec/builtin_tools/` | 先测纯 helper；CLI 只做关键路径 smoke/契约测试 |

### 1.1 `libs/` — 纯函数优先

当前重点模块：`hashing.py`、`md_yaml.py`、`path_refs.py`。

**测试要求**：
- `parse_frontmatter`：无 frontmatter、空 frontmatter、非法 YAML、body 内含 `---`、Unicode
- `update_frontmatter`：更新已有 key、补充新 key、保留 body
- `compute_hash` / `compute_dir_hash`：稳定性、差异性、模板替换只影响 `.md`
- `update_references_in_dirs`：只改命中的 markdown 文件，不改无关文件

### 1.2 `core.py` — 共享枚举与模板能力

`core.py` 当前负责状态枚举、模板复制、根目录查找、stdio fallback 等跨模块能力。

| 函数/能力 | 必测场景 |
|-----------|---------|
| `render_template` | 基本替换、多占位符、缺失 key 变空串、占位符内空格容错、重复占位符 |
| `normalize_status` | canonical 值、常见别名（含中文）、大小写不敏感、未知值原样返回 |
| `find_sspec_root` | 空目录→`None`；根目录命中；子目录向上查找；`.sspec/` 缺少 `project.md` 时不命中 |
| `copy_template` | 文件替换、目录递归复制 |
| `list_template_skills` | 空目录、安全过滤、只返回含 `SKILL.md` 的目录 |
| `configure_stdio_error_fallback` | 在支持 reconfigure 的流上不抛异常，并把 `errors='replace'` 生效 |

### 1.3 `skill_installer.py` — 链接与 gitignore 契约

这是独立的一层，不属于普通 services。

**测试重点**：
- `normalize_legacy_strategy`：旧值归并到 `link|copy`
- `check_path_link` / `remove_path_link`：真实目录、symlink/junction、目标校验
- `install_batch`：`prefer_symlink=False` 直接 copy；link 失败回退 copy；写入 gitignore fence
- `update_skill`：link 策略重建链接；copy 策略全量覆盖目录

### 1.4 `services/` — 主战场

所有 service 公共函数至少覆盖：
1. 一个正向路径
2. 一个边界/错误路径
3. 每个关键分支至少一个断言

共享规则：
- 使用 `tmp_path` 或临时 `.sspec/` 骨架，禁止依赖真实仓库路径
- 禁止 mock `Path.read_text` / `Path.write_text` / `Path.exists` 这类文件系统行为
- 辅助函数可放测试文件顶部，前缀 `_`，并带简短 docstring

#### 重点 service 契约

| 模块 | 必测行为 |
|------|----------|
| `change_service.py` | change 创建、名称规范化、状态别名、进度统计、归档、引用改写、校验 |
| `request_service.py` | request 创建/解析、模糊匹配、link 到 change、archive 引用改写 |
| `ask_service.py` | ask 名称规范化、YAML 模板、预填答案、YAML/legacy `.py` 兼容、转 `.md`、archive |
| `agents_service.py` | 根 `AGENTS.md` 不存在/无标记/有标记/`dry_run` 行为 |
| `meta_service.py` | `.meta.json` 读写、schema migration、未来版本防护、默认值补齐 |
| `project_init_service.py` | 目录骨架、hub skills、meta 初始字段、根 `AGENTS.md` 创建 |
| `project_update_service.py` | meta 准备、legacy 迁移、orphan skill 检测、更新候选状态、hub `.gitignore` 同步 |
| `cmd_service.py` | registry roundtrip、命令去重、脚本 `copy/move/ref`、`resolve_invoke`、缺失脚本错误 |
| `skill_service.py` | skill metadata 解析、列出 hub skills、dominate 合并/冲突/重链语义 |
| `tmp_service.py` | 临时文件/目录创建、默认扩展名、重复名报错 |
| `editor_service.py` | `.env` > `SSPEC_EDITOR` > `EDITOR` 的解析优先级 |

### 1.5 `commands/` — 选择性测试，不追求覆盖率

`commands/` 仍然是薄壳，但当前仓库已经有一批命令层行为测试，这些测试是合理的。

**应该测**：
- 参数校验与错误信息（例如 skill location 校验）
- 与 service 的关键路由/分支（例如 archive 联动、ask 已完成提示）
- 命令层独有逻辑（交互兜底、输出前的状态判定）

**不应该测**：
- Rich 颜色、表格样式、文案空格
- Click/Questionary 自身已保证的框架行为

### 1.6 `builtin_tools/` — helper 优先，CLI 只测关键路径

例如：
- `mdtoc.py`：测 heading 解析、fence 跳过、source 解析
- `view_tree.py`：测 filter/helper，不必强耦合 Rich tree 的完整视觉输出
- `pack_zip.py`：测 gitignore / include / exclude 决策
- `apply_patch.py`：测 patch 解析、失败输出目录、冲突行为

---

## 2. 反模式清单

### 2.1 ❌ 断言存在性代替断言行为

```python
def test_template_dir():
    assert get_template_dir().exists()
```

应改成验证具体契约，例如模板目录内关键文件存在、模板渲染后产生预期结果。

### 2.2 ❌ 绑定实现细节而不是接口

不要把内部时间戳格式、排序实现、表格样式当作行为契约，除非它们确实对外承诺。

### 2.3 ❌ 无意义 smoke test

```python
def test_collect_update_candidates_smoke():
    assert collect_update_candidates(...)
```

必须断言具体 `status`、数量、路径或输出条件。

### 2.4 ❌ 为覆盖率而重复测试同一路径

相同行为用一个测试或 `parametrize` 覆盖，不要复制 3 个只换输入字面量的函数。

### 2.5 ❌ 过度 mock 文件系统

本项目优先真实临时目录。Mock 只用于：
- 外部子进程
- 平台相关 link 行为难以稳定复现时的边界分支
- 编辑器/终端交互等外部系统

---

## 3. 测试文件组织

### 3.1 命名规则

| 测试文件 | 对应范围 |
|----------|----------|
| `test_core.py` | `src/sspec/core.py` |
| `test_hashing.py` / `test_md_yaml.py` / `test_path_refs.py` | `src/sspec/libs/` |
| `test_*_service.py` | 对应 `src/sspec/services/*_service.py` |
| `test_skill_installer.py` | `src/sspec/skill_installer.py` |
| `test_*command*.py` / `test_archive_linked_commands.py` / `test_project_skill_loc_validation.py` | 命令层行为与跨命令流程 |

允许存在跨模块流程测试，只要它验证的是对外行为而不是内部实现细节。

### 3.2 fixture 约定

- `tmp_project`：带最小 `.sspec/` 骨架的项目目录
- `sspec_root`：`tmp_project / '.sspec'`
- 需要完整 init/update 行为时，直接调用对应 service，不要手写重复逻辑

### 3.3 测试类与辅助函数

- 同一函数的测试可放入同一个 `Test<FunctionName>` class
- 辅助函数放文件顶部，前缀 `_`
- helper 只负责降噪，不隐藏断言重点

---

## 4. 可选依赖与命令层导入

当前 `services/` 层不应依赖 `questionary`；交互依赖主要在 `commands/` 层。

如果命令层测试在某些环境下缺少可选交互依赖，采用 **文件级** `skipif`，不要在每个测试函数上重复标记。

```python
try:
    from sspec.commands import project
    HAS_COMMAND_DEPS = True
except ImportError:
    HAS_COMMAND_DEPS = False

pytestmark = pytest.mark.skipif(
    not HAS_COMMAND_DEPS, reason='command-layer optional deps not available'
)
```

---

## 5. 新增/修改代码时的测试义务

当新增或修改 `libs/`、`core.py`、`skill_installer.py`、`services/` 中的 public 行为时，必须同步新增或更新测试。

最少检查清单：
1. 一个典型成功路径
2. 一个边界或错误路径
3. 每个关键分支至少一个验证
4. 若有状态别名/多输入变体，用 `parametrize` 覆盖代表样本

命令层和 builtin tools 不要求 100% 覆盖，但新增对外契约时必须有测试证明它成立。

---

## 6. 运行方式

```bash
# 全量
uv run pytest tests -v

# 单文件
uv run pytest tests/test_change_service.py -v

# 单测试
uv run pytest tests/test_core.py::TestNormalizeStatus::test_canonical_change_statuses -v

# 带覆盖率（若安装 pytest-cov）
uv run pytest tests --cov=sspec --cov-report=term-missing
```

测试必须：
- 不依赖网络
- 不依赖真实用户项目状态
- 不污染仓库根目录
- 在 Windows 环境下也能稳定运行
