# 🚀 SAGE Tutorials - Quick Start

欢迎来到 SAGE Tutorials！本指南将帮助你在 **5 分钟内**开始使用 SAGE。

## ⚡ 超快入门（2 分钟）

### 1. 运行第一个示例

```bash
cd /path/to/sage-tutorials
python L1-common/hello_world.py
```

恭喜！你已经运行了第一个 SAGE 程序！

### 2. 理解架构

SAGE 采用 **5 层架构**，从底层到应用层：

```
L1: Common      → 基础工具 (配置、日志)
L2: Platform    → 平台服务 (调度、部署)
L3: Kernel/Libs → 核心引擎 + 算法库 (流处理、RAG、Agents)
L4: Middleware  → 数据服务 (向量数据库、时序数据库)
L5: Apps        → 完整应用 (端到端解决方案)
```

### 3. 选择学习路径

根据你的角色选择合适的路径：

| 角色          | 推荐路径           | 时间     |
| ------------- | ------------------ | -------- |
| 🔰 初学者     | L1 → L2 基础       | 1-2 小时 |
| 🚀 应用开发者 | L1 → L2 → L3 → L4  | 4-6 小时 |
| 🧠 平台开发者 | 全栈学习 L1-L5     | 1-2 天   |
| 🏗️ 架构师     | 全部 L1-L5 + tools | 2-3 天   |

______________________________________________________________________

## 📚 分层学习指南

### L1: Common - 基础层（15 分钟）

**目标**：理解 SAGE 的基础概念

```bash
cd L1-common
python hello_world.py        # 最基础的示例
```

**核心概念**：

- SAGE 环境配置
- 日志系统
- 基本术语

👉 **下一步**：进入 L2-platform 学习平台服务

______________________________________________________________________

### L2: Platform - 平台层（1-2 小时）

**目标**：理解平台服务与远程环境

#### 2.1 平台服务入门（30 分钟）

```bash
cd L2-platform/environment
python remote_env.py            # 远程环境
```

**核心概念**：

- 平台服务抽象
- 远程环境管理

👉 **下一步**：进入 L3-kernel 学习核心引擎

______________________________________________________________________

### L3: Kernel/Libs - 核心层（2-4 小时）

**目标**：掌握核心引擎与算法库

#### 3.1 Kernel - 批处理与流处理（1-2 小时）

```bash
cd L3-kernel/batch
python hello_local_batch.py   # 本地批处理
python hello_remote_batch.py  # 远程批处理

cd L3-kernel/stream
python hello_streaming_world.py  # 基础流处理
python hello_onebyone_world.py   # 单条流处理
```

#### 3.2 Libs - RAG/Agent/Embedding（1-2 小时）

```bash
cd L3-libs/rag
python simple_rag.py                # 简单 RAG

cd L3-libs/agents
python basic_agent.py               # 基础智能体

cd L3-libs/embeddings
python embedding_demo.py            # 嵌入演示
```

**核心概念**：

- DataStream API
- 批处理 vs 流处理
- RAG/Agents/Embeddings

👉 **下一步**：进入 L4-middleware 学习数据服务

______________________________________________________________________

### L4: Middleware - 中间件层（1-2 小时）

**目标**：使用数据服务与中间件

#### 4.1 服务入门（15 分钟）

```bash
cd L4-middleware
python hello_service_world.py  # 理解服务模型
```

#### 4.2 Memory Service（30 分钟）

```bash
cd L4-middleware/memory_service
python rag_memory_service.py   # RAG 内存服务
```

#### 4.3 数据库服务（30 分钟）

```bash
cd L4-middleware/sage_db
python workflow_demo.py        # 向量数据库

cd L4-middleware/sage_tsdb
python basic_dag_example.py    # 时序数据库
```

**核心概念**：

- Service API
- 向量数据库
- 时序数据处理
- 内存管理

👉 **下一步**：进入 L5-apps 构建应用

______________________________________________________________________

### L5: Apps - 应用层（1-2 小时，高级）

**目标**：理解平台级应用

```bash
cd L5-apps
# (待添加完整应用示例)
```

**核心概念**：

- 应用编排
- 端到端流程设计
- 生产级集成

👉 **下一步**：探索完整应用示例（即将推出）

______________________________________________________________________

## 🎯 常见学习路径

### 路径 1：RAG 开发者（最热门）

```
1. L1-common/hello_world.py              (5 分钟)
2. L3-kernel/batch/hello_local_batch.py  (15 分钟)
3. L4-middleware/memory_service/         (30 分钟)
4. L3-libs/rag/simple_rag.py             (30 分钟)
5. L3-libs/rag/usage_4_complete_rag.py   (1 小时)
```

**总时间**：约 2.5 小时

### 路径 2：Agent 开发者

```
1. L1-common/hello_world.py              (5 分钟)
2. L3-kernel/stream/                     (30 分钟)
3. L3-libs/agents/basic_agent.py         (30 分钟)
4. L3-libs/agents/workflow_demo.py       (1 小时)
```

**总时间**：约 2 小时

### 路径 3：平台工程师

```
1. 完整学习 L1-L3                        (3 小时)
2. L4-middleware/ 全部                   (2 小时)
3. L5-apps/ 全部                         (2 小时)
```

**总时间**：约 7 小时

______________________________________________________________________

## 📖 文档和帮助

### 快速查询

- **快速参考**：`L3-libs/unlearning/docs/QUICK_REFERENCE.md`
- **故障排除**：`L3-libs/unlearning/docs/TROUBLESHOOTING.md`
- **边界约束**：`docs/BOUNDARY.md`
- **可复现检查**：`docs/REPRODUCIBILITY_CHECKLIST.md`
- **学习路径**：`docs/LEARNING_PATH.md`（即将推出）

### 层级文档

每个层级目录都有详细的 README：

- `L1-common/README.md`
- `L2-platform/README.md`
- `L3-kernel/README.md`
- `L3-libs/README.md`
- `L4-middleware/README.md`
- `L5-apps/README.md`

### 遇到问题？

1. 查看 `L3-libs/unlearning/docs/TROUBLESHOOTING.md`
1. 检查每个示例的注释
1. 阅读对应层级的 README
1. 查看项目主 README

______________________________________________________________________

## 🎓 学习建议

### ✅ 推荐做法

1. **按顺序学习**：从 L1 开始，逐层深入
1. **动手实践**：运行每个示例，修改参数
1. **阅读注释**：示例中有详细的说明
1. **理解概念**：不要只运行，要理解原理

### ❌ 避免

1. **跳过基础**：L1-L2 是必须的
1. **只看不做**：一定要运行代码
1. **贪多嚼不烂**：一次专注一个主题

______________________________________________________________________

## 🚀 下一步行动

根据你的兴趣选择：

- **我想构建 RAG 系统** → 按"路径 1"学习
- **我想开发 Agent** → 按"路径 2"学习
- **我想深入理解架构** → 从 L1 开始系统学习
- **我只想快速尝试** → 运行 `hello_world.py` 和几个感兴趣的示例

______________________________________________________________________

## 💡 小贴士

- 每个示例都可以独立运行
- 示例之间有依赖关系，建议按推荐顺序学习
- 遇到错误先查看 `TROUBLESHOOTING.md`
- 配置文件在 `config/` 目录

______________________________________________________________________

**开始你的 SAGE 之旅吧！🎉**
