---
revision: 2
date: 2026-04-18T21:21:57
trigger: "review-feedback"
---

<!-- @RULE: trigger values: review-feedback | discovery | scope-expansion | correction
本文件记录 design gate 后的范围/设计变更。
spec.md 和 design.md 基线不可变，所有后续演化通过此类文件记录。
文件命名：revisions/NNN-description.md（编号递增）。 -->

# fix-create-idempotence-and-clean-unused-patch-status

## Reason
在 review 阶段对实现进行独立检查后，发现两处值得固化修正：一是 `PatchApplyResult.status` 中声明了未被任何代码路径使用的 `invalid_operation_body`，实现与声明不一致；二是 `CREATE` 在已存在文件上的幂等判断采用字面换行比较，在 Windows CRLF 场景下可能把“内容相同的再次应用”误判为 `file_exists`。同时，operation 到 marker 的反向映射在展示层重复出现，适合顺手去重。

## Changes

### Spec Impact
- `CREATE` 的“相同内容 => already_applied”语义细化为：换行风格差异不影响幂等判定，按规范化后的文本内容比较。
- 结果状态集合移除未实际使用的 `invalid_operation_body`，保持声明与实现一致。
- 展示层允许用共享的 operation→marker 常量复用现有 marker 输出，不改变外部行为。

### Design Impact
- `apply_patch()` 的 `CREATE` 分支在比较已存在文件内容时，先将文件内容归一化为 `\n` 再与 patch 内容比较。
- `PATCH_OPEN_MARKERS` 增加对应的 `OPERATION_TO_MARKER` 常量，供 preview 和 failed bundle 输出共用。
- parse-time 对 CREATE/OVERWRITE 上半区非空白的处理继续走 `parse_error` 聚合路径；因此删除未落地的专用 status，而不是引入新的 parse-status plumbing。

### Task Impact
- 修改 `src/sspec/builtin_tools/apply_patch.py`：删除未使用状态、补充 `OPERATION_TO_MARKER`、修正 CREATE 的换行幂等比较。
- 运行轻量校验：`py_compile`、`ruff check`、以及针对 CREATE CRLF 幂等的手动 smoke check。
