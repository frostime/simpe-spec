---
name: design-template
created: 2026-03-17 19:42:43
status: DOING
attach-change: .sspec/changes/26-03-17T20-28_design-template/spec.md
tldr: ''
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: design-template

## Background
<!-- Current situation, background information -->
当前版本的 sspec 在 design 阶段给定了非常明确的模板；这个模板主要为了确保能让“用户理解未来 Agent 会怎么完成这个项目”以便于在“接口”层面理解 agent 对未来更改的声明。
同时另一方面，也是由于一些 Agent model 能力孱弱，如果不给出明确的模板逻辑，只会写出一堆垃圾设计文档，导致用户无法实现人机对齐（Align）

## Problem
<!-- What is not working or missing -->
但是同时我也注意到，当前的模板规定有些死板，
当前版本相当于只应用了两种设计模板： single vs root 。

single 模板实现 new feature code 的场景下好用，但是在其他场景下则不一定。
> Users review designs for: **interfaces**, **data types**, **data flow**, and **logic flow**.
在面对比如设计文档、优化样式等方面，还是按照模板来就有些削足适履

具体问题 Agent 可以参考 当前的 SKILL 还有 archived 的旧 change。

例如典型例子：.sspec/changes/archive/26-03-06T23-39_refresh-spec-docs
这个是个纯粹的文档型 change，但是还是机械地遵循了 Interface Design 的模板，虽然说也能用，但是总感觉看上去怪怪的。


## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

要解决这个问题，如果什么都不考虑自然是提供无数的模板，但是这样会导致 SKILL 无限膨胀。在实操层面不可取。

我的一个初步想法是：
- 在 design 阶段加入一个步骤让 Agent 自行思考 design 当中可以包含哪些小节
- 给出默认推荐的 Atomic 小节的设计模板
- 再给出一些常见场景案例下的设计组合模式
- 具体的规则可以考虑拆分 sub skill 文件，也可以考虑配合 howto 指令（便于批量披露，howto 可以同时接受多种参数）
- 这个想法有点像是模仿 handover 中 Memory 里面，给出推荐的写法，然后自行组织选择不同类型

## Success Criteria
<!-- The conditions or criteria that indicate
the problem has been resolved and meets the user's intention -->

- spec.md 的要点在于：方便用户和 Agent 对齐想法；并且能让用户看到就能理解未来会怎么调整；就像看到 JSON Schema 就知道 API 调用代码会怎么写一样。
- 兼容过去在 implement feature code 上的良好表现，同时大大强化其他方面的表现。

## Relational Context
<!-- Constraints, preferences, related filelinks -->

- src/sspec/templates/skills/sspec-design/
- .\.sspec\changes\archive\**\spec.md
  - `sspec tool fileinfo .\.sspec\changes\archive\**\spec.md`

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.

注意：上面那个想法是不成熟的，只是一个引子，我希望 Agent 独立思考结合经验，和用户讨论再定下最终方案
