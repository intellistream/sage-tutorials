# sage-tutorials 边界清单（Phase 1）

## 仓库定位

`sage-tutorials` 是 L6 教程仓库，职责是提供 **分层示例与学习路径**，不承载生产运行时实现。

## In Scope

- L1-L5 教程示例与讲解文档
- 面向学习者的最小可运行脚本
- 分层依赖规则说明与反例提示
- 教程复现步骤与验收记录

## Out of Scope

- 生产级运行时/服务能力实现
- 各子仓库内部实现细节重构
- API 向后兼容层（shim / re-export / fallback）
- 作为其他仓库依赖入口的稳定 SDK 承诺

## Forbidden Imports / Patterns

- 在教程层新增 `ray` 依赖或 `ray` 运行指引
- 低层示例导入高层实现（违反 L5→L4→L3→L2→L1）
- 为迁移保留临时兼容层（含静默 fallback）

## 跨层调用与动态导入盘点（Phase 1）

- 盘点范围：`README.md`、`QUICK_START.md`、`L1-common` ~ `L5-apps`
- 结论：
  - 教程叙事整体符合分层结构
  - 存在过时 `ray` 文本指引（已在 Phase 1 清理）
  - 存在中间件示例层级标注错误（已修正为 L4）

## 依赖审计（文档依赖 vs 运行时 import）

- 本仓库为教程仓库，当前无 `pyproject.toml` 核心依赖声明
- 审计方法：
  - 以示例代码 import 与 README/QUICK_START 运行指引对齐为准
  - 优先保证说明与示例一致，避免“文档宣称可运行但步骤过时”
- 结论：
  - 未发现新增重依赖声明漂移
  - 已移除/替换旧运行时指引（`ray`）

## Phase 1 子改造清单（可独立 PR）

- [x] PR-A：分层叙事与边界文档补齐（D1）
- [x] PR-B：清理过时步骤与兼容性说明（D2）
- [x] PR-C：建立最小可复现检查清单（D3）
- [ ] PR-D：补齐自动化 smoke 检查脚本（后续）
