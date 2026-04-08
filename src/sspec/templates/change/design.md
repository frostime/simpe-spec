---
change: "{{CHANGE_NAME}}"
created: {{TIME}}
---

# Design: {{CHANGE_NAME}}

<!-- 本文件记录技术设计详情。创建条件：
变更涉及新接口定义、数据模型变更、或架构逻辑改动。
简单 bugfix/文案修改不需要此文件。 -->

<!-- QUALITY BAR (不可违反):
用半结构化、形式化的表达替代平铺直叙的纯文本。
核心目标：提高信息密度，降低不确定性，提高用户理解效率。
一句话：能展示的不要叙述 (show, don't describe)。

常见手段 (非穷举):
- typed code block: 接口、类型、Schema、配置、prompt...
- ASCII diagram: 调用链、状态机、模块树、内容大纲...
- table: before/after 对比、选项权衡、scope 映射...
- labeled items: 多项变更标注 (Fix A / Feat B / Step 1...)
- 伪代码、决策树、约束列表等同样有效

Anti-pattern:
  ❌ "我们将添加一个接受 X 返回 Y 的函数"
  ✅ `def process(x: Input) -> Output: ...`

  ❌ "请求先经过 A 模块处理，然后传递给 B"
  ✅ request → A.validate() → B.process() → response
-->

<!-- 按变更性质组织本文档。没有固定章节要求。
以下是不同类型变更的参考组织方式 (选用，不强制):

Feature/Bugfix  → 接口签名 + 行为流程 + 数据模型
Refactor        → Before/After 结构对比 + 迁移步骤
文档/模板       → 内容大纲 + 章节层级
Prompt/规则     → Before/After 示例 + 决策逻辑
配置/Schema     → Schema 定义 + 迁移路径 + 兼容性策略
-->

<!-- @REPLACE -->
