审查范围与方法
- 范围：c7d82f047f06155c2adeeb713608b4af2869507f..HEAD，仅 src/sspec/（14 个文件，约 +378/-86）
- 方法：我自己通读了 git diff，并 fork 了 3 个独立 subagent 分别从 meta/migration、skill 流程、builtin tools 三个角度做质量与 bug 审查（他们的结论与我这里的结论已交叉验证）
---
严重问题（需要修，属于“引入错误/行为风险”）
- 重复/不可达代码（确定是引入的错误）
  - src/sspec/services/skill_service.py:379、src/sspec/services/skill_service.py:380
  - 现状：create_skill_in_hub() 结尾有两行完全相同的 return CreateSkillResult(...)，第二行不可达。
  - 影响：功能上不一定立刻坏（测试也可能覆盖不到），但这是明确的代码质量/正确性瑕疵，后续维护容易误判，也可能触发更严格的 lint 规则。
- meta_schema 解析过于“自愈”，可能对“已声明但不可解析”的 schema 做错误迁移（有潜在数据破坏）
  - src/sspec/services/meta_service.py:97（_compare_schema）与 src/sspec/services/meta_service.py:160（future schema 检查）
  - 现状：如果 .meta.json 里存在 meta_schema: "2.0-beta" 这类非纯数字版本字符串，_parse_schema() 会返回 None，随后 _compare_schema() 会把它当成 (0,0)，从而走“旧版迁移”路径并执行 key rename / pop（例如移除 schema_version）。
  - 风险：这违背了“未来 schema 应拒绝以避免数据丢失”的意图，且可能对未知/实验版本的 meta 做 destructive 变换。
  - 建议方向：仅当 schema 缺失时才当 0.0；若 schema 字段存在但不可解析，应 ValueError（让 CLI 友好报错）。
- project update 可能在大量 unknown 状态下仍输出 “All files are up to date”，并且迁移-only 写回不补齐 hashes，导致项目长期卡在“unknown”
  - 触发逻辑：src/sspec/commands/project.py:393 到 src/sspec/commands/project.py:403
  - 原因：unknown 默认不会加入 actions（除非 --force），所以当 .meta.json 缺失/file_hashes 为空时，候选往往是 unknown，actions 仍为空，于是走早退并打印“up to date”。同时 migration-only 分支只写 meta_schema/sspec_schema/updated_at/sspec_version，不重建 file_hashes。
  - 影响：用户会被误导为“已同步”，但实际上 update 无法安全更新任何东西（持续 unknown）。
  - 建议方向：早退条件至少要考虑 unknown/modified 的存在；并且当 file_hashes 缺失/为空时，应在 update 过程中把“可验证为 current 的项”写回 file_hashes（把项目恢复到可更新状态）。
- load_meta() 现在可能抛出 ValueError，而多个非 project-update 路径未做 CLI 友好处理（可能出现 traceback/命令崩溃）
  - 抛错源：src/sspec/services/meta_service.py:160，调用点：src/sspec/services/meta_service.py:207
  - 风险调用点举例（未 catch ValueError）：
    - src/sspec/commands/skill.py:18（_record_dominate_location() 里调用 load_meta()）
    - src/sspec/services/skill_service.py:375（create_skill_in_hub()）
    - src/sspec/services/project_init_service.py:282（sync_skill_locations()）
  - 影响：当用户的 .meta.json 来自更新版本 sspec（meta_schema 更高）时，这些命令可能直接异常退出；目前只有 project update 做了友好报错（src/sspec/commands/project.py:262）。
  - 建议方向：要么让 load_meta() 永不抛（返回 {} 或 defaulted meta），把 strict 行为放到 update pipeline；要么在这些命令层统一捕获并转成 ClickException。
---
中等问题（不一定立刻坏，但很值得改）
- --skill-loc 从 Choice 变成 free string 后，缺少路径校验，允许写出项目根目录
  - src/sspec/commands/project.py:107（--skill-loc type=str）
  - 实际使用：src/sspec/services/project_init_service.py:68（targets.append(project_root / loc / 'skills')）
  - 风险：用户可以传 --skill-loc ..、--skill-loc C:\\temp 等，导致 init/sync 在项目外创建/覆盖目录（这是行为面/安全面风险，且是这次 diff 引入的开放输入面）。
  - 也同样影响交互输入：src/sspec/commands/project.py:89（提示“相对路径”，但未强制）。
- skill_locations 的路径分隔符不一致（\\ vs /）会制造重复、并让策略 key 不稳定
  - init 写入：src/sspec/services/project_init_service.py:200（str(rel_loc)，Windows 下是反斜杠）
  - dominate 写入：src/sspec/commands/skill.py:16（.as_posix()，正斜杠）
  - 影响：同一个位置可能同时存在 .claude\\skills 与 .claude/skills，对去重、显示、以及 skill_install_strategies 的 key 一致性都不利。
  - 建议方向：统一存储为 POSIX（as_posix()），迁移时可选做 normalize。
- sspec skill dominate 对 “already linked” 的情况不记录 meta（可能导致 update 漏同步）
  - src/sspec/commands/skill.py:153（status == 'skipped' 直接 return，未调用 _record_dominate_location）
  - 影响：用户明明已经把目录 dominated 成功（历史操作），但 meta 未记录该 location，后续 project update 依赖 skill_locations 时可能遗漏。
---
低风险/主要是质量调整（总体 OK）
- src/sspec/builtin_tools/mdtoc.py：类型标注与 option 格式化（基本无行为改动）。潜在小风险是运行时若有人对函数做 typing.get_type_hints() 可能因 click 未在模块全局导入而 NameError（通常不触发）。
- src/sspec/builtin_tools/pack_zip.py：主要是清理 lint（unused var/import，raise ... from e）。subagent 提到的 zip 路径分隔符 / pathspec 语义问题更多是“原本就有的设计缺陷”，这次 diff 没有直接改变行为（但确实值得后续专门修）。
- src/sspec/services/change_service.py、src/sspec/services/request_service.py：sorted(list(set(...))) -> sorted(set(...)) 属于无行为差异的简化。
- src/sspec/skill_installer.py：主要是格式化（无语义变更）。
---
结论（关于“没有引入错误”）
- 我无法给出“完全没有引入错误”的结论：src/sspec/services/skill_service.py:380 的重复 return 是确定的引入错误（虽不一定立刻导致功能失败，但属于明显瑕疵）。
- 另外 meta_schema 的“不可解析即当 0.0”属于潜在破坏性迁移风险，建议尽快修正以匹配你设定的策略（future schema 必须拒绝）。
如果你希望我下一步继续：我可以基于这份 review 提一个“最小修复清单”（只修高严重度、避免扩大范围），并把每条修复对应到具体测试/行为验证点。
