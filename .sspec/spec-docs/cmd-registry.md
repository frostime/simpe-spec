---
name: Command Registry
description: Define `.sspec/commands/registry.yaml`, script storage strategies, and execution semantics for `sspec cmd`
updated: 2026-03-07
scope:
  - /src/sspec/services/cmd_service.py
  - /src/sspec/commands/cmd.py
  - /tests/test_cmd_service.py
deprecated: false
replacement: ""
---

# Command Registry

## Overview

`sspec cmd` 提供项目级命令注册功能。
它把命令元数据持久化到 `.sspec/commands/registry.yaml`，并按策略管理关联脚本文件。

## On-Disk Layout

```text
.sspec/
└── commands/
    ├── registry.yaml
    └── <optional managed scripts>
```

`registry.yaml` 是唯一真源；命令列表、脚本路径和执行模板都从这里读取。

## Registry Schema

```yaml
commands:
  test:
    description: Run the full test suite
    type: cmd-line
    invoke: uv run pytest tests -v

  deploy:
    description: Run deploy script
    type: script
    invoke: python {script} --env prod
    script_file: deploy.py
    script_strategy: copy
```

字段语义：
- `description`：用户可读说明
- `type`：`cmd-line` 或 `script`
- `invoke`：最终 shell 模板
- `script_file`：脚本文件路径；仅 `script` 类型使用
- `script_strategy`：`copy` / `move` / `ref`，默认 `copy`

## Script Strategy Contract

| 策略 | 存储行为 | `script_file` 记录值 |
|------|----------|----------------------|
| `copy` | 复制到 `.sspec/commands/` | 复制后的文件名 |
| `move` | 移动到 `.sspec/commands/` | 移动后的文件名 |
| `ref` | 不复制、不移动 | 项目内脚本存相对路径；项目外脚本存绝对路径 |

冲突规则：
- `copy` / `move` 目标同名时自动追加 `_1`、`_2` 等后缀
- `remove_command()` 删除 `copy` / `move` 管理的脚本；`ref` 不删除源文件

## Resolve and Execute Flow

```mermaid
graph TD
    A[load_registry] --> B[lookup CommandInfo]
    B --> C[resolve_invoke]
    C --> D[replace {script} if needed]
    D --> E[append extra args]
    E --> F[subprocess.run shell=True cwd=project_root]
```

执行规则：
- 所有命令都以项目根目录作为 `cwd`
- `script` 模式下，`{script}` 会被解析后的脚本路径替换
- 附加参数直接拼接到 `invoke` 尾部
- 脚本不存在时，`run_command()` 抛 `FileNotFoundError`

## Name and Uniqueness Rules

- registry key 就是命令名
- `add_command()` 禁止重复名称，冲突时抛 `CommandExistsError`
- `remove_command()` 找不到命令时抛 `CommandNotFoundError`

## Suggested Invoke Patterns

服务层为常见脚本扩展名提供默认 invoke 模板：

| 后缀 | 模板 |
|------|------|
| `.py` | `python {script}` |
| `.ps1` | `pwsh -File {script}` 或回退 `powershell -File {script}` |
| `.sh` / `.bash` | `bash {script}` |
| `.bat` / `.cmd` | `{script}` |

这只是建议值；最终持久化内容以用户确认后的 `invoke` 为准。

## Testing Requirements

- registry 读写 roundtrip
- 命令增删与重复名错误
- `copy` / `move` / `ref` 三种脚本策略
- `resolve_invoke()` 的 `{script}` 替换与 extra args 拼接
- 脚本缺失时的执行错误

## References

- [Testing Standards](./testing-standards.md) — `cmd_service.py` 的测试义务
