# Project Specifications

此目录存放会跨多个 change 复用的 **项目级持久规范**。
它记录运行时契约、磁盘结构、同步策略、测试规则，以及未来 Agent 需要反复查阅的设计决策。

## 当前规范一览

| 文件 | 主题 | 用途 |
|------|------|------|
| `builtin-tools.md` | Builtin Tools System | 记录 `sspec tool` 的注册模型、工具清单、扩展边界 |
| `skill-installation.md` | SKILL Installation & Sync | 记录 hub-spoke skill 安装、更新、迁移、gitignore 契约 |
| `meta-json.md` | Project Metadata | 记录 `.sspec/.meta.json` schema、迁移、update 保证 |
| `testing-standards.md` | Testing Standards | 记录测试分层、行为契约和反模式 |
| `change-lifecycle.md` | Change Lifecycle | 记录 `.sspec/changes/` 目录结构、状态解析、归档与引用更新 |
| `interaction-records.md` | Interaction Records | 记录 request / ask 文件格式、链接、完成、归档语义 |
| `cmd-registry.md` | Command Registry | 记录 `.sspec/commands/registry.yaml` 与脚本策略 |
| `agents-sync.md` | Root AGENTS Sync | 记录根目录 `AGENTS.md` 中受管 SSPEC block 的同步规则 |

## 何时新增或更新 spec-doc

- 代码引入了跨多个 change 复用的长期契约
- 某个 on-disk schema、目录结构、同步行为不再适合只靠源码理解
- 一项规则已经超出 `project.md` Notes 的简短记忆范畴
- 现有 spec-doc 中的事实陈述已与当前代码不一致

## 编写规则

- 遵循 `write-spec-doc` SKILL，而不是把 spec-doc 写成 changelog
- 单文件 spec-doc 必须带 frontmatter：`name`、`description`、`updated`、`scope`
- `scope` 要列出真实代码路径，至少覆盖主要实现和测试
- 文档必须写当前行为，不写历史过程；历史过程留给 git 和 change 记录
- 修改 spec-doc 时，同步更新 `updated` 字段和本目录索引

## 结构约定

- `README.md` 是目录索引和维护说明，允许不带 frontmatter
- 普通 spec-doc 优先使用单文件；只有主题过大时才拆目录
- 多文件规范使用 `index.md` 作为入口，并在 frontmatter 中列出子文件

```text
spec-docs/
├── README.md
├── change-lifecycle.md
└── large-topic/
    ├── index.md
    ├── part-a.md
    └── part-b.md
```

## Agent 指南

- 开始实现前，先看 `.sspec/project.md` 的 Spec-Docs Index，再进入这里找对应规范
- 发现规则漂移时，优先更新对应 spec-doc，不要把长期知识只写在 handover 里
- 一次 change 如果新增了长期契约，应把 spec-doc 更新视为同一 change 的收尾工作
