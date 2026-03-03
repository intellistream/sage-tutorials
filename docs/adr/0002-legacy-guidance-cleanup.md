# ADR 0002: 过时步骤与兼容性说明清理

- Status: Accepted
- Date: 2026-03-03
- Related: #3, #5

## Context

历史教程文本中仍包含旧运行时指引（如 `ray` 命令）和不一致路径，导致用户按文档执行时产生偏差。

## Decision

- 将 `L3-kernel/cpu_node_demo.py` 中 `ray` 操作说明替换为 Flownet-first/`sage` 运行时语义
- 清理示例日志配置中的 `ray` logger 名称
- 将 `QUICK_START.md` 初始路径统一为本仓库根目录（`/path/to/sage-tutorials`）

## Consequences

- 教程说明与当前架构方向一致
- 新用户复现成本降低，旧流程误导减少
