# 教程端到端可复现检查清单

适用范围：`sage-tutorials` 仓库的分层示例（L1-L5）。

## 环境前置

- 使用已配置的非-venv Python 环境（如 conda）
- 仓库根目录执行：

```bash
cd /path/to/sage-tutorials
python --version
```

## 最小 Smoke 检查（必做）

```bash
# L1: 基础层
python L1-common/hello_world.py

# L3: 核心层（批处理）
python L3-kernel/batch/hello_local_batch.py

# L4: 中间件层（服务入门）
python L4-middleware/hello_service_world.py
```

## 文档一致性检查（必做）

- `README.md` 与 `QUICK_START.md` 路径一致
- 不包含过时 `ray` 操作指引
- 边界规则与示例层级描述一致（参考 `docs/BOUNDARY.md`）

## 验证记录模板

| 项目 | 命令 | 结果 | 备注 |
| --- | --- | --- | --- |
| L1 smoke | `python L1-common/hello_world.py` | ☐ Pass / ☐ Fail |  |
| L3 smoke | `python L3-kernel/batch/hello_local_batch.py` | ☐ Pass / ☐ Fail |  |
| L4 smoke | `python L4-middleware/hello_service_world.py` | ☐ Pass / ☐ Fail |  |
| 文档一致性 | 手工检查 | ☐ Pass / ☐ Fail |  |
