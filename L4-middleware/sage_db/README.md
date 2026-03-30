# SAGE-DB Examples

本目录包含两类与 `sage_flow` 风格一致的 SAGE-DB 示例：

1. 应用（Application）方式：`hello_sage_db_app.py`

   - 直接使用 `SageDB` Python API，插入少量向量后进行一次查询

1. 服务（Service）方式：`hello_sage_db_service.py`

   - 以微服务形式封装 SAGE-DB，注册到 `LocalEnvironment` 后由外部推入向量并执行查询

## 运行前置

SAGE-DB (SageVDB) 已独立为 PyPI 包。如未安装，可运行：

```bash
# 方式 1: 直接安装 SageVDB
pip install isage-vdb

# 方式 2: 安装主仓 + 向量库适配器
pip install isage>=0.3.0
pip install isage-vdb
```

## 运行示例

应用方式：

```bash
python examples/service/sage_db/hello_sage_db_app.py
```

服务方式：

```bash
python examples/service/sage_db/hello_sage_db_service.py
```

## 说明

- Canonical Python API 由独立适配器包 `isage-vdb` 提供
- 当前建议通过显式安装依赖来运行示例，而不是依赖 `packages/*/src` 的本地路径注入
- 若你需要对外暴露更丰富的接口，可在 `python/micro_service/sage_db_service.py` 基础上扩展（如批量删除、索引保存/加载、带条件过滤的查询等）
