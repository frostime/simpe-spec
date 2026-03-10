---
created: '2026-03-09T23:50:01'
name: add_howto_cli_design
why: Design gate for the HOWTO CLI change. The request explicitly asks for deeper
  design work before implementation, and SSPEC requires user alignment before planning.
---

**Ask**: add_howto_cli_design

# User Answer #

- 首先我不建议增加覆盖，这非常危险；如果检测到覆盖应该直接 warning 并跳过
- 另外请问数据模型中的 `slug` 是啥意思?
- 加一个 `howto new` 也 Ok
  - 其实我是不知道是否能设计出可变参数，我是觉得 `howto read <name>` 很难看；但是 `howto <name>` 之后又担心占用了 new, list 等 sub command 的位置；你可以思考怎么解决
- 此外在这个 change 的末尾建议考虑和用户讨论加入第一批内置的 howto

# Agent Question History #

add-howto-cli 设计对齐：

**Context**
我已经创建 change，并完成了第一版设计草案：
- 变更目录：`.sspec/changes/26-03-09T23-41_add-howto-cli/`
- 设计文件：`.sspec/changes/26-03-09T23-41_add-howto-cli/spec.md`

**当前提案**
1. 新增单命令读取入口：`sspec howto <name>` / `sspec howto --list`
2. 官方 HOWTO 放在包内 `src/sspec/howto/`
3. 用户 HOWTO 放在项目内 `.sspec/howto/`
4. 运行时合并两类 HOWTO；若同名，则项目 HOWTO 覆盖内置 HOWTO
5. HOWTO 为轻量只读文档机制；首版不加入 `new/sync/install` 等额外生命周期命令
6. frontmatter 主要支持：`name` + 可选 `desc`，同时兼容 `description`

**我认为这样设计的原因**
- 与 SKILL 分层：HOWTO 只承担“细粒度规则披露”，不承担能力安装或复杂工作流
- 易扩展：后续若要拆更多碎规则，只需新增 markdown 文档，不必改 AGENTS 或 SKILL 结构
- 易定制：项目可覆盖内置 HOWTO，而无需 fork sspec

**需要你确认**
你是否认可这版设计进入下一步 planning？

如果你想调整，请尽量直接指出：
- 是否保留“项目覆盖内置”的优先级
- 官方 HOWTO 是否应放在 `src/sspec/howto/`，还是你更想放到别的位置
- 首版是否要坚持“只读”，还是现在就一起加 `howto new` 之类的能力