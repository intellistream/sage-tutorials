# SAGE Unlearning - 故障排查指南

## 常见错误和解决方案

### 1. ImportError 和依赖问题

#### 错误 1.1: `ModuleNotFoundError: No module named 'sage'`

**症状:**

```
ModuleNotFoundError: No module named 'sage'
  File "usage_1_direct_library.py", line 5, in <module>
    from sage.libs.privacy.unlearning import UnlearningEngine
```

**原因:** SAGE 库未安装

**解决方案:**

```bash
# 方法 1: 在 SAGE 根目录安装
cd /home/shuhao/SAGE
pip install -e packages/sage-libs

# 方法 2: 或者完整安装
make install

# 方法 3: 验证安装
python -c "from sage.libs.privacy.unlearning import UnlearningEngine; print('OK')"
```

**预防:**

- 始终在虚拟环境中工作
- 运行代码前检查依赖: `pip list | grep sage`

______________________________________________________________________

#### 错误 1.2: `ImportError: cannot import name 'BaseFunction'`

**症状:**

```
ImportError: cannot import name 'BaseFunction' from 'sage.kernel'
```

**原因:**

- SAGE 运行时未安装（usage_2, 3, 4 需要）
- 或版本不兼容

**解决方案:**

```bash
# 安装完整 SAGE
pip install -e packages/sage-kernel
pip install -e packages/sage-middleware

# 验证
python -c "from sage.kernel.api.function.base_function import BaseFunction; print('OK')"
```

**预防:**

- usage_1 不需要 SAGE 运行时
- usage_2-4 需要 `sage-kernel`
- 查看 README.md 的依赖清单

______________________________________________________________________

#### 错误 1.3: `ModuleNotFoundError: No module named 'neuromem'`

**症状:**

```
ModuleNotFoundError: No module named 'neuromem'
  File "usage_3_memory_service.py", line 8
    from sage.middleware.components.sage_mem.neuromem import MemoryManager
```

**原因:** NeuroMem 组件未安装（usage_3, 4 需要）

**解决方案:**

```bash
# 安装中间件
pip install -e packages/sage-middleware

# 或单独安装向量库
pip install faiss-cpu
# 或 GPU 版本
pip install faiss-gpu

# 验证
python -c "from sage.middleware.components.sage_mem.neuromem.memory_manager import MemoryManager; print('OK')"
```

**预防:**

- usage_1, 2 不需要 NeuroMem
- usage_3, 4 才需要 VDB

______________________________________________________________________

### 2. 数据和计算错误

#### 错误 2.1: `ValueError: shapes (100, 128) and (127, 128) not aligned`

**症状:**

```
ValueError: shapes (100, 128) and (127, 128) not aligned
  at engine.unlearn_vectors()
```

**原因:** 向量维度不匹配

**解决方案:**

```python
# ❌ 错误
vectors = np.random.randn(100, 128)  # 100 个向量
forget_vectors = np.random.randn(10, 127)  # 维度不同!

# ✓ 正确
vectors = np.random.randn(100, 128)
forget_vectors = vectors[:10]  # 从同一数据源取样

# ✓ 或者
forget_vectors = np.random.randn(10, 128)  # 维度相同
```

**调试技巧:**

```python
print(f"All vectors shape: {vectors.shape}")
print(f"Forget vectors shape: {forget_vectors.shape}")
assert vectors.shape[1] == forget_vectors.shape[1], "维度不匹配!"
```

______________________________________________________________________

#### 错误 2.2: `RuntimeError: CUDA out of memory`

**症状:**

```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB.
```

**原因:** 向量过多或维度过高

**解决方案:**

方式 1: 减少向量数量

```python
# ❌ 原始
vectors = np.random.randn(10000000, 1024)  # 太多了!

# ✓ 修改
vectors = np.random.randn(100000, 1024)  # 降低数量
```

方式 2: 使用 CPU

```python
# 强制使用 CPU
import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

# 或在创建时指定
engine = UnlearningEngine(epsilon=1.0, device="cpu")
```

方式 3: 分批处理

```python
batch_size = 10000
for i in range(0, len(vectors), batch_size):
    batch = vectors[i : i + batch_size]
    result = engine.unlearn_vectors(...)
```

______________________________________________________________________

#### 错误 2.3: `ValueError: epsilon must be positive`

**症状:**

```
ValueError: epsilon must be positive, got -1.0
```

**原因:** 隐私预算参数无效

**解决方案:**

```python
# ❌ 错误
engine = UnlearningEngine(epsilon=-1.0)  # 负数!
engine = UnlearningEngine(epsilon=0)  # 零!

# ✓ 正确
engine = UnlearningEngine(epsilon=1.0)  # 正数
engine = UnlearningEngine(epsilon=0.5)  # 更严格的隐私
engine = UnlearningEngine(epsilon=5.0)  # 宽松的隐私

# 参考值
# epsilon < 0.1: 非常严格
# epsilon 0.1-1.0: 严格（推荐）
# epsilon 1.0-5.0: 中等
# epsilon > 5.0: 宽松
```

______________________________________________________________________

#### 错误 2.4: `OverflowError: cannot convert float infinity to integer`

**症状:**

```
OverflowError: cannot convert float infinity to integer
  in privacy_accountant.compute_epsilon()
```

**原因:** 向量全为零或包含 NaN

**解决方案:**

```python
# 检查数据质量
print(f"含 NaN: {np.isnan(vectors).any()}")
print(f"含 Inf: {np.isinf(vectors).any()}")
print(f"全零向量: {np.allclose(vectors, 0).any()}")

# ✓ 清理数据
vectors = np.nan_to_num(vectors)  # NaN → 0
vectors = np.clip(vectors, -1e6, 1e6)  # 裁剪极值
vectors = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)  # 归一化
```

______________________________________________________________________

### 3. SAGE Framework 错误

#### 错误 3.1: `RuntimeError: No active environment`

**症状:**

```
RuntimeError: No active environment found.
```

**原因:** 未创建 SAGE 环境

**解决方案 (usage_2 中):**

```python
# ❌ 错误
from sage.kernel.api.environment.local_environment import LocalEnvironment

# 直接使用 Pipeline，没有环境

# ✓ 正确
env = LocalEnvironment("my_env")
env.from_source(...).map(...).sink(...)
env.submit()
```

______________________________________________________________________

#### 错误 3.2: `AttributeError: 'NoneType' object has no attribute 'execute'`

**症状:**

```
AttributeError: 'NoneType' object has no attribute 'execute'
```

**原因:** Function 返回 None 或未初始化

**解决方案:**

```python
# ❌ 错误
class MyFunction(BaseFunction):
    def execute(self, data):
        # 缺少返回值!
        pass


# ✓ 正确
class MyFunction(BaseFunction):
    def execute(self, data):
        return data  # 必须返回某些东西
```

______________________________________________________________________

#### 错误 3.3: `KeyError: 'collection_name'` (usage_3 中)

**症状:**

```
KeyError: 'collection_name'
  in service.forget_with_dp("collection_name", ...)
```

**原因:** Collection 不存在

**解决方案:**

```python
# ❌ 错误
service = DPMemoryService()
service.forget_with_dp("docs", ["id_1"])  # docs 不存在!

# ✓ 正确
service = DPMemoryService()
service.create_collection("docs")  # 先创建
service.store_memory("docs", "id_1", vector)  # 再存储
service.forget_with_dp("docs", ["id_1"])  # 再遗忘
```

**调试代码:**

```python
# 列出所有 collections
collections = service.manager.list_collections()
print(f"Available collections: {collections}")

# 检查 collection 是否存在
if not service.manager.has_collection("docs"):
    service.create_collection("docs")
```

______________________________________________________________________

### 4. 性能问题

#### 问题 4.1: 代码运行非常慢

**症状:**

```
# 处理 1000 个向量花费 > 1 分钟
result = engine.unlearn_vectors(...)  # 卡住...
```

**诊断:**

```python
import time

# 计时
start = time.time()
result = engine.unlearn_vectors(...)
elapsed = time.time() - start

print(f"Time: {elapsed:.2f}s")
print(f"Throughput: {len(vectors) / elapsed:.0f} vectors/sec")

# 预期值
# usage_1: > 10k 向量/秒
# usage_3: > 1k 向量/秒
# usage_4: > 500 向量/秒
```

**原因和解决方案:**

| 原因                  | 症状               | 解决方案                    |
| --------------------- | ------------------ | --------------------------- |
| 使用 CPU 处理大量向量 | 很慢 (< 100 vec/s) | 使用 GPU 或减少向量数       |
| 向量维度过高          | 慢 (< 1k vec/s)    | 降低维度或批处理            |
| 过度精度计算          | 很慢               | 使用 float32 而不是 float64 |
| VDB 索引未优化        | 慢 (usage_3/4)     | 重建索引或调整参数          |

______________________________________________________________________

#### 问题 4.2: 内存占用很高

**症状:**

```
# 内存使用超过预期
# 处理 100k 向量时占用 > 20GB
```

**诊断:**

```python
import tracemalloc

tracemalloc.start()

result = engine.unlearn_vectors(...)

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1e9:.2f} GB")
print(f"Peak: {peak / 1e9:.2f} GB")

# 预期值
# 100k × 128 向量（float32）: ~50MB
# + 临时缓冲: ~100-200MB
# 总计应该 < 500MB
```

**解决方案:**

```python
# 方案 1: 分批处理
batch_size = 10000
for i in range(0, len(vectors), batch_size):
    batch = vectors[i : i + batch_size]
    result = engine.unlearn_vectors(batch)

# 方案 2: 使用内存映射
import numpy as np

vectors = np.memmap("vectors.npy", dtype=np.float32, shape=(1000000, 128))

# 方案 3: 使用更小的数据类型
vectors = vectors.astype(np.float16)  # 减半内存
```

______________________________________________________________________

### 5. 隐私和安全问题

#### 问题 5.1: 隐私预算不足

**症状:**

```
PrivacyBudgetError: Remaining budget (0.01) < required (0.1)
```

**原因:** 太多遗忘操作耗尽隐私预算

**解决方案:**

```python
# 方案 1: 增加初始预算
engine = UnlearningEngine(epsilon=10.0)  # 而不是 1.0

# 方案 2: 批量遗忘（更高效）
# ❌ 低效: 单个遗忘 × 100
for vector_id in forget_ids:
    engine.unlearn_vectors(...)

# ✓ 高效: 一次批量遗忘
forget_vectors = vectors[forget_ids]
engine.unlearn_vectors(forget_vectors, forget_ids)

# 方案 3: 监控预算
print(f"Remaining budget: {engine.privacy_accountant.get_remaining_epsilon()}")
```

**最佳实践:**

```python
# 预先规划预算
total_epsilon = 1.0  # 总预算
num_operations = 100  # 预计操作数
epsilon_per_op = total_epsilon / num_operations

engine = UnlearningEngine(epsilon=epsilon_per_op)

# 或使用自适应预算
remaining = total_epsilon
for operation in operations:
    engine.epsilon = remaining / len(remaining_operations)
    engine.unlearn_vectors(...)
    remaining -= consumed
```

______________________________________________________________________

#### 问题 5.2: 无法验证遗忘效果

**症状:**

```
遗忘后的向量与原始向量仍然相似
```

**诊断和解决方案:**

```python
from sklearn.metrics.pairwise import cosine_similarity

# 计算相似度
similarity = cosine_similarity([original_vector], [perturbed_vector])[0, 0]
print(f"Similarity: {similarity:.4f}")

# ✓ 好的遗忘 (相似度低)
# similarity < 0.7 表示有效遗忘

# 调试
if similarity > 0.7:
    # 方案 1: 增加扰动强度
    result = engine.unlearn_vectors(..., perturbation_strategy="aggressive")

    # 方案 2: 增加邻居补偿
    result = engine.unlearn_vectors(..., apply_compensation=True)

    # 方案 3: 使用更强的隐私机制
    from sage.libs.privacy.unlearning.privacy_mechanisms import GaussianUnlearning

    result = engine.unlearn_vectors(..., privacy_mechanism=GaussianUnlearning())
```

______________________________________________________________________

### 6. 使用建议和最佳实践

#### 6.1 一般最佳实践

```python
# 1️⃣ 总是检查输入
assert vectors.shape[1] == expected_dim, "维度错误"
assert not np.isnan(vectors).any(), "包含 NaN"
assert len(vector_ids) == len(vectors), "ID 数量不匹配"

# 2️⃣ 启用日志
import logging

logging.basicConfig(level=logging.DEBUG)

# 3️⃣ 使用错误处理
try:
    result = engine.unlearn_vectors(...)
except ValueError as e:
    print(f"Invalid input: {e}")
except PrivacyBudgetError as e:
    print(f"Privacy budget exceeded: {e}")

# 4️⃣ 验证输出
assert result.success, f"Unlearning failed: {result.error}"
assert result.num_vectors_unlearned == len(forget_ids)

# 5️⃣ 记录关键指标
print(f"Privacy cost: {result.privacy_cost}")
print(f"Perturbation magnitude: {result.metadata['perturbation_magnitude']}")
print(f"Effectiveness: {result.metadata.get('effectiveness', 'N/A')}")
```

______________________________________________________________________

#### 6.2 调试清单

运行代码前检查：

```python
□ 所有必要的依赖已安装
□ 数据格式正确（shape, dtype）
□ 无 NaN 或 Inf 值
□ 隐私参数有效（epsilon > 0）
□ Collection 已创建（usage_3/4）
□ 向量已归一化（如需要）
□ 内存足够
□ GPU 可用（如使用）
```

______________________________________________________________________

#### 6.3 测试模板

```python
def test_unlearning():
    # 准备
    np.random.seed(42)
    vectors = np.random.randn(100, 128).astype(np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    ids = [f"doc_{i}" for i in range(100)]

    # 创建引擎
    engine = UnlearningEngine(epsilon=1.0)

    # 执行
    result = engine.unlearn_vectors(
        vectors_to_forget=vectors[:10],
        vector_ids_to_forget=ids[:10],
        all_vectors=vectors,
        all_vector_ids=ids,
    )

    # 验证
    assert result.success
    assert result.num_vectors_unlearned == 10
    assert result.privacy_cost[0] <= 1.0

    # 效果检查
    for i, forgotten_id in enumerate(ids[:10]):
        orig = vectors[i]
        perturbed = result.metadata["perturbed_vectors"][i]
        similarity = np.dot(orig, perturbed)
        assert similarity < 0.9, f"Insufficient perturbation for {forgotten_id}"

    print("✓ All tests passed")


if __name__ == "__main__":
    test_unlearning()
```

______________________________________________________________________

### 7. 获取更多帮助

**文档:**

- 📖 README.md - 总体概况
- 📋 QUICK_REFERENCE.md - 快速参考
- 📊 COMPARISON_MATRIX.md - 详细对比
- 🔧 各个 usage\_\*.py 文件中的详细注释

**代码示例:**

- `usage_1_direct_library.py` - 直接库用法
- `usage_2_sage_function.py` - SAGE Function
- `usage_3_memory_service.py` - VDB 集成
- `usage_4_complete_rag.py` - 完整系统

**调试技巧:**

```python
# 启用详细日志
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 添加自定义日志
logger = logging.getLogger(__name__)
logger.debug(f"Vector shape: {vectors.shape}")
logger.info(f"Unlearning {len(forget_ids)} vectors")
logger.warning(f"Privacy budget: {remaining_budget}")
```

**常见资源:**

- SAGE 官方文档: docs/
- 版本变更记录: CHANGELOG.md
- API 参考: 源码中的 docstring

______________________________________________________________________

**更新历史**

- v1.0: 初始版本，涵盖常见错误和解决方案
