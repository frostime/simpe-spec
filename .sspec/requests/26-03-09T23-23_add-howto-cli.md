---
name: add-howto-cli
created: 2026-03-09 23:23:10
status: DONE
attach-change: .sspec/changes/26-03-09T23-41_add-howto-cli/spec.md
tldr: 'Added a HOWTO CLI plus a first batch of concise agent-facing HOWTO documents.'
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: add-howto-cli

## Background
<!-- Current situation, background information -->
当前的 sspec 项目的规则主要依赖于 Agnets.md + SKILL
但是我注意到这两种规则披露机制都不够灵活细粒度。

我的想法是再自定义增加一个更加细粒度的规则披露机制，叫做 HOWTO-CLI。

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

**How TO 文档**
- 模仿 SKILL 的样子，设计中名为 HOWTO 的文档，大致的定义如下
```md
---
name: xxx
desc: xxx
---

内容
```
一个 howto 往往对应一个非常具体的规则，通常字数应该控制在 1K 字之内
name 上明明应该以动词开头，表明这是一个操作指南，尽量做到看到 `how to <name>` 就能知道这是在干什么
desc 是可选的参数，通常是对内容的总结或者补充说明

**HOW TO CLI**
```
sspec howto <name>
```

用户可以通过 `sspec howto <name>` 来查看对应的 HOWTO 文档内容

有一些保留参数: `--list` 用于列出所有的 HOWTO 文档

**HOWTO 的注册**

类似SKILL，以文档为中心注册
分为两类:

- 内置的，可以在 sspec 下创建一个 howto 目录，放置一些官方的 howto 文档
- 用户自定义, 在 .sspec/howto/*.md 中

## Success Criteria
<!-- The conditions or criteria that indicate
the problem has been resolved and meets the user's intention -->

需要地功能能正常运行；并且 howto 后续也方便扩展

注：后续我打算基于 howto 机制拆分一些 sspec 地用法出来，更有利于渐进式披露一些细碎地的则用法

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.

注意：我个人认为这是一个重要的想法，所以请你深入思考帮我完善这个方案的设计。
