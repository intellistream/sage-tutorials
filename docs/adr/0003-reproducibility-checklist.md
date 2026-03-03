# ADR 0003: 教程端到端可复现检查清单

- Status: Accepted
- Date: 2026-03-03
- Related: #3, #6

## Context

教程仓库需要提供统一的“最小可复现”标准，避免示例可读但不可运行。

## Decision

- 新增 `docs/REPRODUCIBILITY_CHECKLIST.md` 作为统一检查入口
- 要求每次大规模文档/示例调整后，至少完成 L1/L3/L4 三层 smoke 复现
- 将检查结果在 issue/PR 中以 checklist 形式回填

## Consequences

- 教程修改具备可追踪验证证据
- 未来可平滑升级为自动化 smoke 脚本
