# L2: Platform - 平台服务层示例

> 当前对应 SAGE surface：`isage` → `sage.runtime`

## 📖 层级说明

**Platform** 层提供平台服务抽象；在当前单仓模型中，这些能力已并入主仓 runtime / foundation：

- 消息队列抽象 (Queue Descriptor)
- KV 存储后端 (Storage Backend)
- 服务基类 (BaseService)
- 调度系统 (Scheduler)

## 📚 目录结构

```text
L2-platform/
├── scheduler/      # 调度系统示例
└── deployment/     # 部署方案示例
```

## 🎯 学习路径

### 1️⃣ 调度系统 (`scheduler/`)

理解任务调度：

- `scheduler_comparison.py` - 调度器对比
- `remote_env.py` - 远程环境

### 2️⃣ 部署方案 (`deployment/`)

生产环境部署（待添加）

## 🎯 学习目标

完成本层示例后，你将掌握：

1. SAGE 的调度机制
1. 本地与可选分布式执行环境
1. 生产部署的最佳实践

## ⏭️ 下一步

学完平台层后，继续学习：

- **L3-kernel/** - 流式执行引擎
- **L3-libs/** - 算法库和工具
