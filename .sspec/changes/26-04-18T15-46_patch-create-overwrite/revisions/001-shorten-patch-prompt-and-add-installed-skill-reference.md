---
revision: 1
date: 2026-04-18T20:39:10
trigger: "review-feedback"
---

<!-- @RULE: trigger values: review-feedback | discovery | scope-expansion | correction
本文件记录 design gate 后的范围/设计变更。
spec.md 和 design.md 基线不可变，所有后续演化通过此类文件记录。
文件命名：revisions/NNN-description.md（编号递增）。 -->

# shorten-patch-prompt-and-add-installed-skill-reference

## Reason
用户接受 CREATE/OVERWRITE 功能本身，但指出 `PATCH_PROMPT` 的主要受众是没有 SKILL 能力的本地/远端 LLM。当前 prompt 仍然偏长，并且没有把“长回复中夹带多个 patch block”这个高实用性场景放到足够清晰的位置。另外，prompt 需要提供当前已安装 `sspec` 版本对应的本地 `write-patch` skill 路径，方便可读本地文件的 agent 深入参考。

## Changes

### Spec Impact
- `Docs E` 的 prompt 同步目标细化为：默认 `PATCH_PROMPT` 优先服务 patch authoring，而不是完整解释全部执行语义。
- `PATCH_PROMPT` 应保留三种 block 语法、关键硬规则、operation 选择规则、以及 multi-block/mixed-text bundle 行为。
- prompt wording 采用 CLI/tool-centered 表达，避免使用 `you` / `I` 叙述视角。
- prompt 末尾新增一个本地 reference 行，指向当前已安装 `sspec` 包中的 `templates/skills/write-patch/SKILL.md` 路径。

### Design Impact
- `src/sspec/builtin_tools/apply_patch.py` 需要从安装包资源解析 `write-patch` skill 路径，并在 `--prompt` 输出时动态拼接到短版 prompt footer。
- prompt 主体改为更短的 authoring guide：使用 ````patch fenced blocks；先列出 SEARCH/CREATE/OVERWRITE 三种 block 形式，再单独说明 multi-block bundles 可以与其他文本交错出现。
- 详细状态语义继续保留在 skill/spec-doc 中；默认 prompt 只保留生成可用 patch 所必需的信息。

### Task Impact
- 新增一项 review feedback 实现：重写 `PATCH_PROMPT` 为短版 bundle-aware authoring guide。
- 新增一项实现：在 `apply_patch.py` 中动态解析当前安装包内 `write-patch` skill 路径，并追加到 prompt 输出。
- 新增一项验证：运行 `sspec tool patch --prompt`，确认输出更短、使用 ````patch、包含 multi-block 说明和 installed-package reference。
