# 对比分析：openspec vs sspec 使用体验

> 分析日期：2026-03-05
> 测试环境：openspec 1.2.0 / sspec (当前 dev)
> 测试目录：`tmp/quicktest_openspec` / `tmp/quicktest_sspec`

---

## 1. 实际体验记录

### 1.1 openspec 初始化体验

```
openspec init . --tools github-copilot
```

**观察到的结构：**

```
.github/
  prompts/              ← slash commands (.prompt.md)
    opsx-apply.prompt.md
    opsx-archive.prompt.md
    opsx-explore.prompt.md
    opsx-propose.prompt.md
  skills/               ← 4 个 agent skills
    openspec-propose/
    openspec-apply-change/
    openspec-archive-change/
    openspec-explore/
openspec/
  changes/
    demo-change/        ← 自动创建的演示 change
      proposal.md
      design.md
      tasks.md
      specs/demo-cap/spec.md
```

**关键 CLI 流程体验：**

```bash
# 1. 创建 change
openspec new change "user-auth"

# 2. 查询状态（JSON API 风格）
openspec status --change "user-auth" --json
# → 返回: 依赖图、artifact 完成状态、applyRequires

# 3. Agent 获取下一步指令
openspec instructions proposal --change "user-auth" --json
# → 返回: context, rules, template, instruction, outputPath, dependencies
```

**最大感受**：CLI 本身就是 Agent 的"任务调度器"。`instructions --json` 返回结构化的 prompt 内容（context + rules + template），Agent 每次只需调用 CLI 就能知道下一步该做什么、按什么模板写。整个流程由 CLI 驱动，SKILL 是流程协调层。

---

### 1.2 sspec 初始化体验

```bash
uv run sspec project init     # quicktest_sspec 已提前初始化
```

**生成的结构：**

```
.sspec/
  project.md            ← 项目身份层（技术栈、路径、约定）
  requests/             ← 用户意图记录
  changes/              ← 每次 change
    <ts>_<name>/
      spec.md
      tasks.md
      handover.md
      reference/
  skills/               ← 按 phase 拆分的 SKILLs
    sspec-research/
    sspec-design/
    sspec-plan/
    sspec-implement/
    sspec-review/
    sspec-handover/
    sspec-ask/
    ...
  spec-docs/            ← 架构级知识文档
  asks/                 ← Q&A 决策记录
AGENTS.md               ← 核心协议（根目录）
```

**关键流程体验：**

```bash
# 1. 用户先写 Request（这是 sspec 的强制性起点）
uv run sspec request new "user-auth"
# → 创建 .sspec/requests/..._user-auth.md，供用户填写 Background/Problem/Direction

# 2. Agent 从 request 创建 change
uv run sspec change new --from .sspec/requests/..._user-auth.md

# 3. 整个 lifecycle 在 AGENTS.md 中定义，Agent 自主切换 phase
```

**最大感受**：用户必须先"做作业"——填写 request 里的各字段，才能把任务交付给 Agent。AGENTS.md 是全局协议手册，Agent 每次都先读它来校准行为。

---

## 2. 核心机制对比

| 维度 | openspec | sspec |
|------|---------|-------|
| **Agent 入口** | 用户输一句话 `/opsx:propose "想法"` | 用户写结构化 request 文件 |
| **CLI 角色** | Runtime 任务调度器（JSON API） | 文件创建工具（utility CLI） |
| **Agent 协议层** | SKILL 文件（每个 SKILL 含完整流程） | AGENTS.md（根协议）+ phase SKILLs |
| **Artifact 流** | proposal → specs → design → tasks（由 CLI 依赖图管理） | spec.md（A+B 合一）→ tasks.md |
| **Context 持久化** | 无显式机制（依赖 proposal/design 文件） | handover.md（强制性 checkpoint） |
| **质量关口** | 内嵌于 SKILL 的 AskUserQuestion | 显式的 @ask 阶段关口（Design/Implement 强制） |
| **探索模式** | 有：openspec-explore（纯思考，禁写代码） | 无（research 是 implementation-oriented） |
| **Schema 定制** | 支持 fork/init 自定义整套 artifact pipeline | 通过 SKILL 内容定制各阶段行为 |
| **多工具支持** | 强（init 时指定 claude/copilot/cursor 等） | 弱（主要针对 VS Code Copilot） |
| **Request 机制** | 无（proposal 是 Agent 生成的 artifact） | 有（request 是用户写的 input document） |

---

## 3. 分析：Agent 视角

### 3.1 openspec 对 Agent 的友好度

**亮点（⭐ 值得学习）：**

1. **`instructions --json` 运行时注入**：Agent 每步只需调用 `openspec instructions <artifact> --json`，就能拿到该 artifact 对应的 context + rules + template + 指令。这是一个优雅的**动态 prompt 工厂模式**——rules 和 template 都存在 CLI/schema 里，SKILL 只定义流程，不硬编码规则文本。

2. **依赖图透明化**：`status --json` 暴露 artifact 依赖图，Agent 无需推断顺序，直接消费机器可读数据。

3. **单次会话完成全部 artifacts**：`openspec-propose` SKILL 设计为"一次 call 完成 proposal + specs + design + tasks"，Agent 可以连续创建完所有 pre-implementation artifacts，无需用户介入。

**弱点：**

1. **会话中断无恢复机制**：openspec 没有 handover.md 等等价物。如果 Agent 会话中断，下次 resume 需要重读所有 artifact 文件，没有明确的"断点"。

2. **跨会话的状态模糊**：没有类似 `project.md` 的项目身份文件，Agent 每次都需要自己推断项目背景。

3. **Agent 主动性过强**：`opsx:propose` 让 Agent 一次性生成全部 artifacts，但缺乏用户 alignment 关口。如果方向偏了，用户在 tasks 阶段才发现，return cost 高。

### 3.2 sspec 对 Agent 的友好度

**亮点：**

1. **AGENTS.md 作为"基准手册"**：Agent 每次从同一入口读起，状态机清晰（read project.md → classify → dispatch）。信息层次（protocol / project identity / phase skill）之间边界清晰。

2. **phase-level 知识隔离**：每个阶段（research/design/plan/implement）的细节在独立 SKILL 文件中，主协议保持简洁。Agent 只在需要时读负责该 phase 的 SKILL，不必一次加载所有规则。

3. **handover.md 降低上下文代价**：明确的断点文档减少了 Agent 重建状态的成本。

**弱点：**

1. **缺乏机器可读的状态模型**：没有 `status --json` 等价物。Agent 通过读 AGENTS.md + spec.md frontmatter 来推断状态，是人类可读而非结构化查询。

2. **SKILLs 文本量大**：sspec-design, sspec-plan 等每个 SKILL 内容丰富，但 Agent 每次都需要完整加载，token 成本高于 openspec 的"按需注入"模式。

---

## 4. 分析：开发者视角

### 4.1 openspec 开发者体验

**使用流程：**
```
/opsx:propose "add user authentication"
→ Agent 问：描述你要构建什么？
→ Agent 自动创建 proposal + specs + design + tasks
→ 用户 review artifacts
→ /opsx:apply
→ Agent 实现代码
→ /opsx:archive
```

**优点：**
- 摩擦力极低。一行指令启动完整流程，适合"想到什么做什么"的快速迭代。
- 不要求用户提前有清晰想法，Agent 会通过 AskUserQuestion 澄清。
- proposal 文件比 sspec 的 request 更接近最终代码的"合同"（明确列 capabilities）。

**缺点：**
- 用户不被强制思考。如果用户想法模糊，Agent 产出的 proposal 也模糊，而用户很可能不认真 review 200 行的 proposal.md。
- 无 request list 作为工作待办列表。开发者难以追踪"我计划做哪些事"。
- 没有 project.md 级别的项目约定层，换 Agent 时需要重新交代背景。

**对开发者技能的要求：** 低。适合 vibe coding，不要求善于表达需求。

### 4.2 sspec 开发者体验

**使用流程：**
```
sspec request new "user-auth"
→ 开发者填写 request.md（Background / Problem / Initial Direction / Success Criteria）
→ 把 request 交给 Agent
→ Agent 读 AGENTS.md → 开始 Research → Design
→ @ask 对齐 spec（MANDATORY）
→ Plan → Implement
→ @ask review（MANDATORY）
→ Handover
```

**优点：**
- Request 是强制 onboarding——写 request 的过程本身是一次思维整理。用户交付 Agent 时已经有清晰的想法。
- spec/tasks 双重可见性：开发者打开 `.sspec/changes/xxx/` 就能以人类可读的方式了解当前状态。
- requests 目录可当 issue tracker / todo list，不需要额外工具。
- 两个强制 @ask 关口（Design align + Implement review）防止 Agent 偏离。
- handover.md 使长 session 后的 resume 快速可靠。

**缺点：**
- 摩擦力高。写一份完整 request 需要 5-10 分钟，简单任务时显得繁重。
- 微任务路径（Micro-change zone）虽然有，但和主流程分离，体验矛盾感强。
- sspec 工具链深度绑定 `uv run sspec`，新用户心智成本不低。

**对开发者技能的要求：** 中-高。需要有能力表达需求、善于结构化思考。

---

## 5. sspec 的开发哲学

### 5.1 核心命题

> **"AI 只是工具，开发者才是 author。"**

sspec 的所有设计选择都指向同一个根：**不让 Agent 成为项目的主导者**。

### 5.2 设计选择的统一逻辑

**① Request-first：强制入口规范化**

- `request.md` 要求用户填写 Background、Problem、Initial Direction、Success Criteria。
- 这不是表单——这是强迫用户在给 Agent 任务之前，先对自己清醒一次。
- 对比 openspec：proposal 是 Agent 生成的，用户只描述一句话。sspec 认为这种"一句话"模式的根本问题是：**用户自己都没想清楚要什么**，怎么能指望 Agent 做对？

**② @ask 阶段关口：显式 alignment**

- Design align（MANDATORY）：在开始写代码前，必须让用户确认方向。
- Implement review（MANDATORY）：写完代码后，必须请用户 review 再结束。
- 这两个关口的本质是：**把 Agent 的自主性限制在明确的边界内**，防止 Agent 自我演化出偏离用户意图的结果。

**③ Handover：抗失忆设计**

- 每个 session 结束时，所有重要发现都记录在 handover.md。
- 这承认了 LLM 有 context window 限制和 session 中断的现实，设计专门的持久化机制来应对。
- 哲学含义：**系统不应该依赖 Agent 的记忆；显式文档才是真相的来源**。

**④ spec.md（A+B 合一）：向开发者暴露全局**

- Section A（Problem）+ Section B（Solution）在同一文件中，开发者一眼能读完一个 change 的全貌。
- 对比 openspec 的 proposal + design 分离，sspec 认为：对于 solo developer，看两个文件 = 两倍的摩擦力。

**⑤ project.md：跨 Agent 的项目记忆**

- 包含 Tech Stack、Key Paths、Conventions、spec-docs index、Notes。
- 任何一个新 Agent（或新 session）读完 project.md 都能快速定位在项目中。
- 这解决了 LLM 的"失忆"问题：**不指望 Agent 记住，而是让知识活在文档里**。

### 5.3 目标用户画像

sspec 不是为所有人设计的。它的目标用户是：

- **有经验的独立开发者**，习惯于在编码前先想清楚
- **对"vibe coding"有警惕心**的人，不喜欢 Agent 自作主张
- **把 AI 作为执行工具而非决策主体**的人
- **需要长期维护项目的人**，关注 context 持久化和状态可见性

### 5.4 核心价值主张

1. **可控性 > 便利性**：宁可流程繁琐，也要保持开发者对项目走向的掌控
2. **显式 > 隐式**：每个状态转换、每个决策、每个发现都要有文档记录
3. **规范入口 > 低摩擦入口**：通过强制 request 机制，提升每次 Agent 任务的质量基线

---

## 6. 改进建议：从 openspec 借鉴

### 6.1 CLI 设计

**建议 A：`sspec change status --json`（借鉴 openspec `status --json`）**

openspec 的 `status --json` 返回结构化的 artifact 状态和依赖图，Agent 可以直接消费机器可读数据——而无需解析 markdown frontmatter。

sspec 目前没有等价物。建议增加：
```bash
sspec change status --json [change-path]
# 返回: { status, phase, tasks_total, tasks_done, last_handover, has_ask_pending }
```

Agent 可以用这个快速判断 change 当前处于什么 phase，tasks 完成度，是否有悬而未决的 ask。

---

**建议 B：`sspec instructions <phase> --json`（借鉴 openspec `instructions --json`）**

openspec 最精妙的设计之一：CLI 作为 Agent 的 rules/template 运行时注入点。当 SKILL 需要更新时，只需更新 CLI（无需重写 SKILL）。

对 sspec 的映射：可以考虑将 spec.md / tasks.md 的填写模板和 rules 从 SKILL 文件中提取出来，通过 CLI 动态注入：
```bash
sspec instructions spec-section-b --change <name> --json
# 返回: { template: "...", rules: [...], context: "..." }
```

这样 sspec 的 SKILLs 可以变得更精简（只描述 flow，不内嵌 template）。

---

**建议 C：`sspec change validate` 完善**

openspec 有 `openspec validate [item]` 命令。sspec 的 `sspec change validate` 已存在，但可以借鉴 openspec 对 spec 和 tasks 的完整性检查（missing sections、空占位符等），提升早期发现问题的能力。

---

### 6.2 AGENTS.md 设计

**建议 D：增加 Explore 模式（借鉴 openspec-explore）**

openspec 有一个专门的 `explore` 模式，它明确声明：
> "Explore mode is for thinking, not implementing. You may read files and investigate, but you must NEVER write code."

这是一个优秀的设计——给 Agent 的行为模式起了名字，并明确划定了边界。

sspec 目前的 Research 阶段是 implementation-oriented 的，没有纯"思考伙伴"模式。建议在 AGENTS.md 中增加：

```markdown
| `@explore [topic]` | 进入探索模式：分析思路、权衡方案、对话思考，**不写代码、不修改文件** |
```

并配套一个 `sspec-explore` SKILL，明确 stance（好奇、不预设结论、用 ASCII 图可视化、可读代码但不写代码）。

---

**建议 E：Micro-change 路径优化**

当前 AGENTS.md 对 Micro task 的处理是：
> "Micro task (≤3 files, ≤30min, obvious) → Do directly, no change needed"

这个判断标准（≤3 files, ≤30min）对 Agent 来说是模糊的。建议参考 openspec 的 schema 概念，为 micro-change 定义更清晰的判定规则，或者在 request.md 的 frontmatter 中增加 `scale: micro | single | multi` 字段，让用户在写 request 时就明确指定，而不是留给 Agent 自行判断。

---

### 6.3 SKILL 设计

**建议 F：sspec-design 加入 Capabilities 映射概念（借鉴 openspec proposal）**

openspec 的 proposal.md 有一个刻意设计的 `Capabilities` section，要求 Agent 列出：
- 新建哪些 specs（每个都会成为 `specs/<name>/spec.md`）
- 修改哪些已有 specs

这个设计非常聪明：**强制用变更前做 API surface 分析**，后续 specs/design/tasks 都基于这个 capability list。

sspec 的 spec.md 缺乏这一层显式的"影响范围声明"。建议在 sspec-design SKILL 或 spec.md 模板中加入：

```markdown
## Affected Scope
<!-- explicit list: which modules / files / interfaces are created/modified/deleted -->
```

这能帮助 Agent 在 design 阶段就对 scope 做出精确声明，而不是隐含在 B. Proposed Solution 里。

---

**建议 G：sspec-research 增加 "investigation depth" 声明**

openspec-explore 打开了一种有价值的研究思路：Agent 可以"进入探索状态"，是思维开放的、不预设结论的。

sspec 的 sspec-research 更像是"为 design 做准备"，目的性很强。建议区分两种 research 场景：
- **Orientating research**: 新人进入陌生代码库，全面扫描
- **Focused research**: 为特定 change 寻找证据和约束

在 sspec-research SKILL 最开头声明当前是哪种类型，会让 Agent 的探索行为更精确。

---

### 6.4 Prompt 文本编写

**建议 H：phase gate 的 @ask 用 `sspec ask` 还是 `question` 工具要更明确**

sspec 的 AGENTS.md§3 已有说明（见 Consultation 表格），但实际上不同用途之间的选择规则有时容易混淆。

openspec-propose SKILL 里有一个值得借鉴的模式，每次 AskUserQuestion 都有明确的  **scenario label**：
```
If no clear input provided, ask what they want to build.
Use the AskUserQuestion tool (open-ended, no preset options) to ask:
> "What change do you want to work on? Describe what you want to build or fix."
```

建议 sspec 的 @ask gate 描述遵循类似模式，每个关口都给出**示例问题模板**，而不只是描述规则。这样 Agent 生成的 @ask 质量更一致。

---

**建议 I：为 sspec-handover 增加"快速 resume card"**

✅ 已完成（以替代方案实现，2026-03-06）：未采用独立 `30-second Resume` 卡片，改为以 `handover.md` 顶部最新 `Session Log` 条目作为唯一 resume 入口，并配合 `Working Memory (Stable)` / root `Sub-Change Status` 实现 30 秒恢复目标。该方案避免了 Resume Card 与日志双重状态漂移。

当前 handover.md 模板很完整，但作为 resume 入口，Agent 需要从头读完。建议在 handover.md 顶部增加一个 30-second-card：

```markdown
## ⚡ 30-second Resume
- Phase: IMPLEMENT
- Next action: Implement task 3 (src/services/auth.py)
- Open question: None
- Risk: DB schema migration requires manual step
```

这是 openspec "status --json reveals applyRequires" 的人类可读版等价物。

---

## 7. 总结

| | openspec | sspec |
|--|---------|-------|
| 核心定位 | AI-native，以 Agent 为中心 | Doc-driven，以开发者为中心 |
| 最大优势 | 极低摩擦，CLI 驱动 Agent | 强可控性，显式状态管理 |
| 最大短板 | 会话断续困难，用户没有提前思考机制 | 摩擦偏高，学习曲线陡峭 |
| 适合场景 | 快速实验、vibe coding、idea → code | 长期项目管理、严肃产品开发 |
| 对 Agent 要求 | 调用 CLI API，按模板填写 | 阅读并理解协议文档、自主 phase 切换 |

**sspec 的哲学本质**：它是一套为"不喜欢 AI 替自己做主"的开发者而设计的**协作规范**。核心价值不在于"让开发更快"，而在于"让开发者始终掌握项目主权"。这使它和 openspec 根本性地站在了两个不同的「用户心智模型」上。

openspec 问："你要什么？"然后去做。
sspec 问："你想清楚了吗？"然后才开始。

---

## 7. 补充分析：YAML 驱动 vs Markdown 驱动

### 7.1 openspec 的 YAML 架构解剖

openspec 的 YAML 有两层：

**层 1：每 change 目录的 `.openspec.yaml`（极简）**

```yaml
schema: spec-driven
created: 2026-03-05
```

仅是个标记文件——指向使用哪个 schema，记录创建时间。真正的"规则"不在这里。

**层 2：全局 `schema.yaml`（核心）**

这才是精髓。每个 artifact 定义：

```yaml
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md        # ← 渲染模板路径
    instruction: |               # ← Agent 填写该 artifact 的指令文本
      Create the proposal document...
    requires: []                 # ← 依赖图

  - id: tasks
    requires: [specs, design]    # ← 依赖图（机器可读）
    ...
apply:
  requires: [tasks]
  tracks: tasks.md               # ← 哪个文件含 checkboxes
```

然后 Agent 调用：

```bash
openspec instructions proposal --change "user-auth" --json
# → 返回: { instruction: "...", template: "...", context: "...", rules: [...] }
```

**关键设计理念**：CLI 是 Agent 的**运行时 rules 注入点**。SKILLs 只描述流程，不硬编码 template 和 rules。更新规则 = 更新 CLI/schema.yaml，无需重写 SKILLs。

值得注意的是：即便如此，openspec 的 `tasks.md` **仍然是 Markdown checkbox 格式**：

```
- [ ] 1.1 Create new module structure
- [ ] 1.2 Add dependencies to package.json
```

openspec 没有把 tasks 移到 YAML。因为 tasks 本质上是给人读的 checklist，YAML 不能更好地表达任务的 prose 说明、分组标题、验证条件。

### 7.2 sspec 的 tasks.md 是否应改为 YAML？

**结论：不建议改 tasks.md 为 YAML，但建议增加独立机器可读状态层**。

#### 分析过程

| 维度 | Markdown tasks.md | YAML tasks |
|------|------------------|------------|
| 人类可读性 | ✅ 直接当 dev dashboard | ❌ 繁琐，需 IDE 渲染 |
| Agent 解析 | ✅ regex `- \[x\]` 已足够 | ✅ 结构化，但过度 |
| 嵌入 prose 说明 | ✅ 自然 | ❌ 强行嵌 YAML 字符串 |
| 手动编辑 | ✅ 勾选即可 | ❌ 需知道 YAML 语法 |
| 机器查询状态 | ❌ 需解析 markdown | ✅ 直接 load |

tasks.md 的核心价值在于"人类可读的执行计划"，这和 YAML 的优势场景（机器可读结构化数据）正交。

#### 真正的问题

sspec 缺少 **机器可读的 change 状态摘要**，导致没有等价于 `openspec status --json` 的能力。解决方案不是改 tasks.md 格式，而是：

**方案：每 change 目录增加 `.state.yaml`（借鉴 openspec 的 `.openspec.yaml`）**

```yaml
# .sspec/changes/<ts>_<name>/.state.yaml
phase: IMPLEMENT         # PLANNING | DOING | REVIEW | DONE | BLOCKED
tasks_total: 12
tasks_done: 5
last_handover: 2026-03-05T14:30
open_asks: 0
```

这样：
- `sspec change status --json` 可以实现（读此文件）
- tasks.md 继续保持 markdown（保留人类可读性）
- Agent 更新任务时顺带更新 `.state.yaml`（or only at handover）

> 💡 更轻量的替代方案：把状态字段加进 `handover.md` 的 frontmatter，不增加新文件。

---

## 8. 补充分析：sspec SKILLs 文本量问题

### 8.1 各 SKILL 规模

```
sspec-design     343 lines  ← 最大
sspec-plan       151 lines
sspec-research    62 lines
sspec-implement   65 lines
sspec-review      63 lines
sspec-handover    61 lines
sspec-ask         88 lines
sspec-mdtoc       63 lines
```

### 8.2 sspec-design 内容分解

| 内容区块 | 行数 | 性质 | 可优化？ |
|---------|-----|------|---------|
| Workflow 流程图 | ~10 | Flow logic | ✅ 必要，精简 |
| Scale assessment 表 | ~15 | Rules | ⚠️ 与 AGENTS.md §2 重复 |
| CLI 命令 (change new) | ~20 | Utility | ⚠️ 与 AGENTS.md §5 重复 |
| Frontmatter YAML 规范 (Step 2.5) | ~50 | Template rules | ⚠️ 与模板文件重复 |
| Section A 写法规则 | ~20 | Writing rules | ✅ 必要 |
| Section B 写法：4条 Presentation Rules | ~90 | Writing rules | ✅ 核心价值，必要 |
| Section B 各子节 skeleton | ~20 | Template | ⚠️ 可外链 |
| Root change spec 规则 | ~60 | Rules | ✅ 必要 |
| @ask 步骤 | ~10 | Flow logic | ✅ 必要 |
| 指向 examples-single.md / examples-root.md | ~5 | References | ✅ 已优化（外链） |

**主要冗余来源：**

1. **Scale assessment 表格在 AGENTS.md§2 和 sspec-design 中都有**：两处都定义了 micro/single/multi 的标准，Agent 如果同时读两个，会重复处理相同规则。

2. **CLI 命令在 AGENTS.md§5 和 sspec-design Step 2 中都列出**：`sspec change new --from <request>` 等命令在主协议和 SKILL 里均有，属于内容重复。

3. **Frontmatter YAML schema (Step 2.5) 是"运行时规则注入"候选项**：这 50 行 YAML 规范本质是模板内容描述，比较适合移到 CLI 的 `instructions` 响应而不是 SKILL 文本。

### 8.3 核心的权衡：冗余 vs 上下文完整性

**反对消除冗余的理由**：

Agent 读 SKILL 时，不一定总是先读过 AGENTS.md（尤其在长对话后 context 被压缩）。SKILL 内容的自包含性（self-contained）意味着 Agent 不需要跨文件拼接上下文就能工作。从这个角度，冗余是"防御性设计"。

**支持消除冗余的理由**：

1. Token 成本：每次读 sspec-design 需要加载 343 lines，而其中 ~30% 是和 AGENTS.md 重复的。
2. 维护成本：Scale assessment 标准如果要更新，现在需要在两处修改，容易不一致。
3. 可读性：SKILL 越简洁，Agent 越能快速定位核心价值（4条 Presentation Rules）。

### 8.4 具体优化建议

#### 建议 J：SKILL = Flow + Core Rules，不重复 AGENTS.md 内容

✅ 已完成（2026-03-06）：`sspec-design` 已将 Scale assessment / CLI quick ref 等重复内容改为引用 `AGENTS.md`，并保留最小兜底提示以降低上下文缺失风险。

将 sspec-design 中与 AGENTS.md 重复的部分替换为链接：

```markdown
## Step 1: Assess Scale
→ See AGENTS.md §2 Scale Assessment table.
```

```markdown
## Step 2: Create Change
→ See AGENTS.md §5 CLI Quick Reference for exact commands.
```

估算可以从 343 行降至 ~240 行（减少约 30%），且保留全部核心写作规则。

---

#### 建议 K：借鉴 openspec 的"instructions 注入"分离 template 内容

openspec 中，spec 的 template 和 instruction 存在 `schema.yaml`，通过 CLI 动态注入。sspec 目前的 SKILL 里内嵌了 template skeleton（如 spec.md 的 Key Design 子节结构、tasks.md 的 Phase Structure）。

建议：将 **"如何填写 spec.md B"** 的 template 内容从 sspec-design SKILL 中提取出来，放入 `src/sspec/templates/change/spec.md` 的 comment 注释（即原本的 `@RULE` annotations），然后 sspec-design 只保留 Rules（4条 Presentation Rules）而不是 skeleton。

这条建议比较激进，需要权衡"SKILL 自包含" vs "SKILL 精简"。目前 sspec 已经通过 `@RULE` comments 在 template 文件里嵌了部分规则，这个方向基本一致。

---

#### 建议 L：sspec-plan 的 Phase Structure template 可外链

✅ 已完成（2026-03-06）：`sspec-plan` 已移除内嵌 Phase Structure 模板，改为指向 `examples.md` / `tasks.md` 模板 `@RULE`（按需查阅）。

sspec-plan 里的 Phase Structure markdown（30行）本质是一个 reference template，和 sspec-design 里的 examples 一样适合外链处理：

```markdown
📚 Phase Structure template: [examples.md](./examples.md#phase-structure)
```

这已经是 sspec-plan 部分区域的做法（`examples.md` 已存在），只需将 SKILL 主体里的 inline template 替换为链接。

---

#### 建议 M：区分"必读内容"和"参考内容"

在 SKILL 顶部明确标记哪些是 Agent 每次必须处理的，哪些是"查阅时才需要"。

```markdown
## REQUIRED (每次必读)
- Workflow | Step 4 (@ask alignment)
- 4 Presentation Rules

## REFERENCE (按需查阅)
- Root change spec rules → §Step 3B
- Frontmatter schema → §Step 2.5
- Examples → [examples-single.md](./examples-single.md)
```

这使得 Agent 在初次加载时只需处理 ~100 行 "required" 内容，其余按需检索。实际上这个模式和 openspec 的 "skills 提供流程 + CLI 提供 template"是同一种分层思维，只不过是在 markdown 文件内部做了分层。

---

## 9. 总结（修订版）

| | openspec | sspec |
|--|---------|-------|
| 核心定位 | AI-native，以 Agent 为中心 | Doc-driven，以开发者为中心 |
| 最大优势 | 极低摩擦，CLI 驱动 Agent，schema 可定制 | 强可控性，显式状态管理，request 规范入口 |
| 最大短板 | 会话断续困难，无 handover，用户无预思考 | 摩擦偏高，SKILL 文本量大，缺机器可读状态 |
| 适合场景 | 快速实验、vibe coding、idea → code | 长期项目管理、严肃产品开发 |
| YAML 用途 | schema.yaml = workflow 定义；.openspec.yaml = change 标记 | spec.md/tasks.md frontmatter = 状态存储 |
| 最值得借鉴 | `instructions --json`（运行时规则注入）；`explore` 模式 | — |

sspec 的核心哲学：**"AI 只是工具，开发者才是 author。"** 所有设计——强制 request、@ask 关口、handover 机制——都是这一哲学的具体实现。

openspec 问："你要什么？"然后去做。
sspec 问："你想清楚了吗？"然后才开始。

---

*End of Report*
