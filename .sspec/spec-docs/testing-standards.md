---
name: testing-standards
description: "sspec 测试编写规范：架构分层策略、质量判定标准、反模式清单"
updated: 2026-02-12
scope:
  - /tests/**
  - /src/sspec/services/**
  - /src/sspec/libs/**
  - /src/sspec/core.py
  - /src/sspec/config.py
deprecated: false
---

# Testing Standards

## 0. 核心原则

测试的唯一目的：**验证行为契约**。一个测试必须回答一个具体问题——"当输入 X 时，系统是否产出 Y？"。无法对应到具体行为契约的测试就是噪声。

判定标准：删掉这个测试后，如果有一类 bug 将不再被捕获，它就是有价值的；如果删掉后什么也不会发生，它就是垃圾。

---

## 1. 架构分层与测试策略

sspec 的代码分为四层，每层的测试策略不同：

```
层级            位置                    测试策略
─────────────────────────────────────────────────────────
libs/           纯函数工具              单元测试（无 I/O 即最优）
core.py         类型 + 共享工具         单元测试
config.py       配置加载               单元测试 + 文件 I/O
services/       业务逻辑               集成测试（tmp_path 文件系统）
commands/       CLI 薄壳               不测（或极少量 smoke test）
```

### 1.1 libs/ — 纯函数优先

`libs/` 下的模块（`hashing.py`, `md_yaml.py`）是纯函数或近纯函数。

**测试要求**：

- 覆盖正常路径 + 所有边界条件
- `parse_frontmatter`：无 frontmatter、空 frontmatter、不完整 frontmatter（单个 `---`）、非法 YAML、非 dict YAML、Unicode、body 中包含 `---`
- `compute_hash`：确定性、不同输入产生不同输出
- `compute_dir_hash`：文件名变更可检测、`.md` 替换仅作用于 `.md` 文件
- 禁止只测 "函数不抛异常" 的空断言

### 1.2 core.py — 类型与工具函数

`core.py` 包含枚举、常量、路径解析、模板渲染、skill 元数据解析。

**测试要求**：

| 函数 | 必测场景 |
|------|---------|
| `render_template` | 基本替换、多占位符、缺失 key 变空串、大括号内空格容错、无占位符文本不变、重复占位符 |
| `normalize_status` | 所有 canonical 值、至少 5 个别名（含中文如 `进行中`→`DOING`）、大小写不敏感、未知值原样返回 |
| `find_sspec_root` | 空目录→None、根目录有 `.sspec/project.md`→命中、子目录向上查找命中、有 `.sspec/` 但无 `project.md`→None |
| `copy_template` | 文件级替换、递归目录复制 |
| `parse_skill_metadata` | 有效 frontmatter、无 frontmatter→`{}`、文件不存在→`{}`、带 replacements |
| `list_skills` | 空目录、目录型 skill、扁平 `.md` skill、排序验证 |
| `get_workspace_skill_targets` | 指定 primary_loc、auto-detect 模式、`.sspec` 始终包含 |

### 1.3 services/ — 集成测试（核心价值区）

**这是测试的主战场。** `services/` 包含所有业务逻辑，且与文件系统交互。

测试规则：
1. **每个 public 函数至少一个正向测试 + 一个边界/错误测试**
2. 使用 pytest `tmp_path` fixture，禁止使用真实文件系统路径
3. 共享 fixture 定义在 `conftest.py`：`tmp_project`（带骨架的项目目录）、`sspec_root`（`.sspec/` 路径）
4. 辅助函数（如 `_set_spec_status`、`_write_tasks`）定义在各测试文件顶部，前缀 `_`

各 service 的具体测试要求：

#### change_service.py

| 函数 | 必测场景 |
|------|---------|
| `create_change` | 创建后三文件齐全 + `reference/` 目录存在；名称规范化（大写→小写、空格→连字符、特殊字符剔除）；空名称抛 `InvalidChangeNameError`；`is_root=True` 产出不同模板内容；同分钟内重复创建抛 `ChangeExistsError` |
| `parse_change` | 默认状态 `PLANNING`；自定义状态读取；别名状态（如 `IN_PROGRESS`→`DOING`）自动规范化；任务进度统计（`done`/`total`）；`<Demo Task>` 排除在进度统计外；PIVOT 关键词检测；BLOCKED 状态检测；`archived` 标记传递 |
| `find_change_matches` | 精确匹配、后缀匹配（`*_name`）、包含匹配、`archive` 目录排除、无结果返回 `[]` |
| `list_changes` | 空项目→`[]`；多 change 返回；默认排除归档；`include_archived=True` 包含归档；结果按名称排序 |
| `archive_change` | 目录移入 `archive/`、原路径消失；spec.md 写入 `archived` 时间戳；同名冲突自动加计数器后缀 |
| `validate_change` | 空目录→报告三文件缺失；模板状态→报告空 section；填充后→对应问题消失 |

#### request_service.py

| 函数 | 必测场景 |
|------|---------|
| `normalize_request_name` | 空格→连字符、特殊字符剔除、已规范化名称不变 |
| `extract_request_name_from_filename` | 新格式（`26-01-02T03-04_name`→`name`）、旧格式（`250102030405-name`→`name`）、纯名称原样返回 |
| `create_request` | 生成文件含 frontmatter（`status: OPEN`、`attach-change: null`）；无效名称抛 `ValueError`；重复抛 `FileExistsError`；带 template 渲染 |
| `find_request_matches` | 精确→后缀→旧格式→包含四级降级匹配；目录不存在→`[]` |
| `parse_request_file` | 标准解析；name 优先取 frontmatter 否则取文件名；tldr 回退到 body 首行；无 frontmatter→`None`；状态别名规范化 |
| `link_request_to_change` | request 写入 `attach-change` 和 `status: DOING`；change spec.md 添加 `reference` 条目；重复 link 不产生重复引用；change 不存在抛 `FileNotFoundError` |
| `archive_request` | 移入 `archive/`；写入 `archived` 时间戳；同名冲突自动后缀 |

#### ask_service.py

| 函数 | 必测场景 |
|------|---------|
| `normalize_ask_name` | 连字符→下划线；特殊字符清除；有变更时返回 warning；无变更时 warning 为 None；空结果抛 `ValueError` |
| `create_ask_template` | 生成 `.py` 文件含 `CREATED/REASON/QUESTION/USER_ANSWER`；同名冲突自动后缀 |
| `execute_ask_prompt` | 预填 `USER_ANSWER` 直接返回（不触发交互）；`.py` 不存在但 `.md` 存在→返回警告；完全不存在→`FileNotFoundError` |
| `save_ask_answer` | 追加 `ANSWER` 变量到文件 |
| `convert_ask_to_md` | 生成 `.md` 含问题和答案；原 `.py` 删除 |
| `find_ask_matches` | 精确、后缀、包含匹配；自动去除 `.md` 后缀 |
| `archive_ask` | 移入 `archive/`；冲突后缀 |

#### agents_service.py

| 函数 | 必测场景 |
|------|---------|
| `update_root_agents_block` | 文件不存在→创建；存在且有 `SSPEC:START/END` 标记→替换中间内容、保留前后内容；无标记→追加；内容已一致→返回 `False`；`dry_run=True` 不写文件；模板不存在→`False` |

#### meta_service.py

| 函数 | 必测场景 |
|------|---------|
| `load_meta` / `save_meta` | 不存在→`{}`；roundtrip 一致性；Unicode；损坏 JSON→`{}`；非 dict JSON→`{}` |

#### project_init_service.py

| 函数 | 必测场景 |
|------|---------|
| `initialize_project` | 完整目录骨架（changes/archive, requests, asks, skills, spec-docs）；`.meta.json` 含必要字段（`schema_version`, `sspec_version`, `file_hashes`, `managed_skills`）；`project.md` 存在；`AGENTS.md` 创建；skills 安装到 hub；`.gitignore` 创建；已存在无 force→`ProjectAlreadyInitializedError`；`force=True` 可重建 |

#### project_update_service.py

| 函数 | 必测场景 |
|------|---------|
| `collect_update_candidates` | 刚初始化→全部 `current`；修改已安装 skill→检测到 `updatable`；空 meta 不崩溃 |
| `collect_orphaned_skills` | 刚初始化→无孤儿；meta 中多出不存在于模板的 skill→检测为孤儿 |

#### cmd_service.py

> `cmd_service.py` 顶层 import 了 `questionary`（通过 `sspec.commands.project`）。测试文件必须用 `try/except ImportError` 守护 import，并在缺少依赖时 `pytest.mark.skipif` 整个文件。

| 函数 | 必测场景 |
|------|---------|
| `load_registry` / `save_registry` | 不存在→`{}`；roundtrip；损坏 YAML→`{}` |
| `add_command` / `remove_command` | 添加→可查到；重复→`CommandExistsError`；删除→查不到 + 脚本文件清理；不存在→`CommandNotFoundError` |
| `handle_script_file` | copy 保留原文件、move 删除原文件、ref 返回路径引用；copy 同名冲突加后缀 |
| `resolve_invoke` | cmd-line 拼接 extra_args；script 模式 `{script}` 替换为绝对路径 |

### 1.4 commands/ — 原则上不测

`commands/` 是 Click 装饰器 + Rich 输出 + Questionary 交互的薄壳。业务逻辑在 `services/`。

例外：如果某个 command 包含无法提取到 service 的复杂逻辑（当前不存在此情况），可以用 `click.testing.CliRunner` 做 smoke test。但不要为了覆盖率而测输出格式。

---

## 2. 反模式清单

以下是**禁止**出现在本项目测试中的模式。

### 2.1 ❌ 断言存在性代替断言行为

```python
# BAD — 只验证"不崩"，不验证行为
def test_template_dir():
    tdir = get_template_dir()
    assert tdir.exists()
```

这类测试在模板目录被重命名、内容被清空时都不会失败。

```python
# GOOD — 验证具体行为契约
def test_template_dir_contains_agents_and_project():
    tdir = get_template_dir()
    assert (tdir / 'AGENTS.md').exists()
    assert (tdir / 'project.md').exists()
```

### 2.2 ❌ 测试实现细节而非接口

```python
# BAD — 绑定到内部时间戳格式
def test_change_dir_name_format():
    path = create_change(sspec_root, 'demo')
    assert re.match(r'\d{2}-\d{2}-\d{2}T\d{2}-\d{2}_demo', path.name)
```

时间戳格式是内部实现。测试应关注 **"创建后三文件齐全"** 而非目录名格式。

### 2.3 ❌ 签名不匹配的死测试

```python
# BAD — 原测试代码中的实际案例
# link_request_to_change 的签名是 (sspec_root, request_file, change_path)
# 但测试传的是 change_name='demo'，根本跑不过
link_request_to_change(
    sspec_root=sspec_root, request_file=req, change_name='demo'
)
```

编写测试前必须 `inspect.signature()` 或阅读源码确认函数签名。

### 2.4 ❌ 无断言的 "smoke test"

```python
# BAD — 跑完就算过，什么都没验证
def test_collect_update_candidates_smoke():
    candidates = collect_update_candidates(...)
    assert candidates  # 只断言非空
```

"非空"不是有意义的行为契约。要断言：candidates 的 `status` 分布、`display_path` 格式、具体数量或具体条件。

### 2.5 ❌ 为覆盖率而写的重复测试

```python
# BAD — 三个测试本质相同
def test_parse_frontmatter_key_value(): ...
def test_parse_frontmatter_another_key_value(): ...
def test_parse_frontmatter_yet_another(): ...
```

同一行为路径只需一个测试。用 `@pytest.mark.parametrize` 覆盖多组输入。

### 2.6 ❌ Mock 过度

本项目使用 `tmp_path` 真实文件系统做集成测试。禁止 mock 文件系统操作（`Path.read_text`, `Path.write_text` 等）。Mock 只用于隔离外部系统（网络、子进程），当前项目中几乎不需要。

---

## 3. 测试文件组织

### 3.1 命名与映射

```
tests/
├── conftest.py                      # 共享 fixture
├── __init__.py                      # 空
├── test_core.py                     # → src/sspec/core.py
├── test_config.py                   # → src/sspec/config.py
├── test_md_yaml.py                  # → src/sspec/libs/md_yaml.py
├── test_hashing.py                  # → src/sspec/libs/hashing.py
├── test_change_service.py           # → src/sspec/services/change_service.py
├── test_request_service.py          # → src/sspec/services/request_service.py
├── test_ask_service.py              # → src/sspec/services/ask_service.py
├── test_agents_service.py           # → src/sspec/services/agents_service.py
├── test_meta_service.py             # → src/sspec/services/meta_service.py
├── test_project_init_service.py     # → src/sspec/services/project_init_service.py
├── test_project_update_service.py   # → src/sspec/services/project_update_service.py
└── test_cmd_service.py              # → src/sspec/services/cmd_service.py
```

一个源文件对应一个测试文件。不做跨模块测试文件。

### 3.2 conftest.py 标准 fixture

```python
@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    """带 .sspec/ 骨架的临时项目目录（不走 init 流程）。"""
    sspec = tmp_path / '.sspec'
    sspec.mkdir()
    for d in ['changes', 'changes/archive', 'requests', 'asks', 'skills', 'spec-docs']:
        (sspec / d).mkdir(parents=True, exist_ok=True)
    (sspec / 'project.md').write_text('# Project\n', encoding='utf-8')
    return tmp_path

@pytest.fixture()
def sspec_root(tmp_project: Path) -> Path:
    return tmp_project / '.sspec'
```

`tmp_project` 手动构建骨架而非调用 `initialize_project`，保证 service 测试不依赖 init 逻辑。`initialize_project` 的测试在 `test_project_init_service.py` 中单独验证。

### 3.3 测试类按函数分组

```python
class TestCreateChange:
    def test_creates_required_files(self, sspec_root): ...
    def test_name_normalization(self, sspec_root): ...
    def test_empty_name_raises(self, sspec_root): ...

class TestParseChange:
    def test_default_status(self, sspec_root): ...
    def test_alias_normalization(self, sspec_root): ...
```

同一函数的测试放在同一个 class 中。class 名 = `Test` + 函数 PascalCase 名。

### 3.4 辅助函数

```python
def _set_spec_status(change_path: Path, status: str) -> None:
    """修改 spec.md frontmatter 中的 status。"""
    ...

def _write_tasks(change_path: Path, done: int, total: int) -> None:
    """生成指定 done/total 的 tasks.md。"""
    ...
```

辅助函数定义在测试文件顶部（fixture 之后、class 之前），前缀 `_`，带 type hints 和单行 docstring。

---

## 4. 可选依赖处理

`cmd_service.py` 通过顶层 import 间接依赖 `questionary`。CI 环境可能未安装。

**处理模式**：

```python
try:
    from sspec.services.cmd_service import (
        CommandInfo, add_command, load_registry, ...
    )
    HAS_CMD_SERVICE = True
except ImportError:
    HAS_CMD_SERVICE = False

pytestmark = pytest.mark.skipif(
    not HAS_CMD_SERVICE, reason='questionary not installed'
)
```

全文件级 skip，不要在每个 test 函数上加 skipif。

---

## 5. 新增函数的测试义务

当新增或修改 `services/`、`libs/`、`core.py` 中的 public 函数时，**必须**同步新增或更新测试。验证清单：

1. 至少一个正向路径测试（典型输入→预期输出）
2. 至少一个边界/错误测试（空输入、None、不存在的路径、重复操作）
3. 如果函数有多个分支（if/elif/try-except），每个分支至少一个测试
4. 如果函数接受枚举/别名，用 `parametrize` 覆盖代表性别名

不需要 100% 行覆盖率。但每个 **行为契约** 必须有对应测试。

---

## 6. 运行方式

```bash
# 全量
PYTHONPATH=src pytest tests/ -v

# 单文件
PYTHONPATH=src pytest tests/test_change_service.py -v

# 单测试
PYTHONPATH=src pytest tests/test_core.py::TestNormalizeStatus::test_canonical_change_statuses -v

# 带覆盖率（需 pytest-cov）
PYTHONPATH=src pytest tests/ --cov=sspec --cov-report=term-missing
```

所有测试必须在 `PYTHONPATH=src` 下通过（editable install 或直接路径引用）。测试不依赖网络、不依赖特定 OS、不依赖全局状态。
