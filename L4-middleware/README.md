# L4: Middleware - 中间件层示例

> 当前对应 SAGE surface：主仓服务接入模式 + 外部适配器 / 迁移说明

## 📖 层级说明

**Middleware** 层现在主要承担两类教学内容：

- 如何在核心 SAGE pipeline 中注册/调用服务
- 如何把向量库、记忆、TSDB 等能力作为外部适配器接回主仓

- Memory Service - 内存管理服务
- SAGE-DB - 向量数据库
- SAGE-TSDB - 时序数据库
- NeuroMem - 神经记忆栈

## 📚 目录结构

```text
L4-middleware/
├── hello_service_world.py  # 服务入门示例
├── memory_service/          # 内存服务示例
├── sage_db/                 # 向量数据库示例
└── sage_tsdb/               # 时序数据库示例
```

## 🎯 学习路径

### 1️⃣ 服务基础

- `hello_service_world.py` - 理解服务模型

### 2️⃣ Memory Service (`memory_service/`)

内存管理和持久化（部分示例已迁移为说明模式）：

- `rag_memory_service.py` - RAG 内存服务
- `rag_memory_pipeline.py` - 内存管道
- `rag_memory_manager.py` - 内存管理器

### 3️⃣ SAGE-DB (`sage_db/`)

向量数据库接入与迁移说明：

- `workflow_demo.py` - 工作流演示

### 4️⃣ SAGE-TSDB (`sage_tsdb/`)

时序数据处理：

- `basic_dag_example.py` - 基础 DAG
- `advanced_dag_example.py` - 高级 DAG
- `stream_join_dag_example.py` - 流连接 DAG

## 🎯 学习目标

完成本层示例后，你将掌握：

1. 如何在主仓 runtime 中组织服务调用
1. 向量数据库的基本操作
1. 时序数据的处理方法
1. 内存管理的最佳实践

## ⏭️ 下一步

学完中间件层后，继续学习：

- **L5-apps/** - 完整应用和解决方案
