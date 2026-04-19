---
name: add-prompt-assemble-tool
created: 2026-04-19 16:14:07
status: DOING
attach-change: .sspec/changes/26-04-19T16-29_add-prompt-assemble-tool/spec.md
tldr: ''
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: add-prompt-assemble-tool

## Require

我打算增加一个 sspec tool，用处是用代码拼接本地代码成一个 Agent/LLM 方便理解阅读的 prompt

### 需求背景 | Why

经常需要和 web 对话页面，和 LLM 对话，就需要引用当前工作空间的源代码、运行结果等

我希望把这个过程自动化，使用一个 sspec tool ... 自动一键生成、读取、拼接成 prompt

可以参考：.sspec/tmp/26-04-19T16-12_prompt拼接起来的demo.md 的效果


## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

在逻辑上抽象三个步骤

- 定义 prompt 集合
- 运行时：
  - 根据 prompt 定义集合，读取当前的结果
  - 拼接成 prompt，并创建临时文件 （sspec tmp），使用 open_editor 打开给 User 查看

至少需要支持这些类型：

- File 内容 （运行时动态读取）
- File Chunk (line range)
- shell command 运行结果
- File Tree 结构

---

同时我在思考是否可以还支持把常见的集合规范缓存为某种 preset 方便直接使用？
——当然也可以不需要，如果有用，直接把 sspec 保存在 shell 文件中也能服用

---

CLI tool 要支持 interactive 模式，能：
- 自动选择类型
- 对文件路径支持自动补全

## Relational Context
<!-- Constraints, preferences, related filelinks -->

- src/sspec/builtin_tools/
- .sspec/tmp/26-04-19T16-12_prompt拼接起来的demo.md

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-clarify` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.
