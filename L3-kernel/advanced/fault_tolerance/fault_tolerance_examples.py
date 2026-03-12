"""Fault tolerance usage examples.

这些示例现在只依赖主仓 `sage` 包，演示如何：

1. 在 `LocalEnvironment` 配置中声明容错策略；
2. 用简单 source/sink 构造可运行示例；
3. 为自定义策略定义清晰的最小协议。

注意：当前示例重点是配置方式与扩展模式，保持 fail-fast，不再依赖已退役的分仓 API。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import yaml

from sage.foundation import SinkFunction, SourceFunction
from sage.runtime import LocalEnvironment, StopSignal


class DemoFileSource(SourceFunction):
    """Simple source that reads lines from a file when available."""

    def __init__(self, config: dict[str, Any] | None = None, **kwargs):
        super().__init__(**kwargs)
        cfg = dict(config or {})
        data_path = cfg.get("data_path") or cfg.get("file_path")
        self._lines = self._load_lines(data_path)
        self._index = 0

    @staticmethod
    def _load_lines(data_path: str | None) -> list[str]:
        if data_path:
            path = Path(data_path)
            if path.exists():
                return [
                    line.rstrip("\n")
                    for line in path.read_text(encoding="utf-8").splitlines()
                ]
        return [
            "What is SAGE?",
            "How do I run sage verify?",
            "Why is stream-first important?",
        ]

    def execute(self, data=None):
        if self._index >= len(self._lines):
            return StopSignal("demo-file-source-finished")
        line = self._lines[self._index]
        self._index += 1
        return line


class DemoTerminalSink(SinkFunction):
    """Simple sink that prints output."""

    def execute(self, data):
        if isinstance(data, StopSignal) or data is None:
            return None
        print(f"OUTPUT> {data}")
        return data


def _load_yaml_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML config must deserialize to a mapping")
    return data


class FaultHandlerProtocol(Protocol):
    def handle_failure(self, task_id: str, error: Exception) -> bool: ...

    def can_recover(self, task_id: str) -> bool: ...

    def recover(self, task_id: str) -> bool: ...


# ============================================================================
# 应用用户示例 - 容错配置对用户是透明的
# ============================================================================


def example_1_user_checkpoint_strategy():
    """
    示例 1: 应用用户使用 Checkpoint 策略

    用户只需在 Environment 配置中声明，无需编写任何容错代码。

    """

    # 创建环境时声明使用 Checkpoint 容错策略
    env = LocalEnvironment(
        "qa_pipeline_with_checkpoint",
        config={
            "fault_tolerance": {
                "strategy": "checkpoint",
                "checkpoint_interval": 60.0,  # 每60秒保存一次
                "max_recovery_attempts": 3,  # 最多恢复3次
                "checkpoint_dir": ".sage/checkpoints",
            },
            "source": {"data_path": "data/questions.txt"},
            "sink": {},
        },
    )

    # 正常定义 DAG - 完全不需要关心容错
    (
        env.from_source(DemoFileSource, env.config["source"])
        .map(lambda x: x.upper())  # 一些处理
        .sink(DemoTerminalSink, env.config["sink"])
    )

    # 提交作业 - 容错由系统自动处理
    # 如果任务失败，系统会自动从最近的 checkpoint 恢复
    env.submit()

    print("✅ Pipeline submitted with checkpoint fault tolerance")


def example_2_user_restart_strategy():
    """
    示例 2: 应用用户使用 Restart 策略

    使用指数退避重启策略，用户同样无需编写容错代码。

    """
    # 使用指数退避重启策略
    env = LocalEnvironment(
        "data_pipeline_with_restart",
        config={
            "fault_tolerance": {
                "strategy": "restart",
                "restart_strategy": "exponential",
                "initial_delay": 1.0,  # 首次重启等待1秒
                "max_delay": 60.0,  # 最多等待60秒
                "multiplier": 2.0,  # 每次延迟翻倍
                "max_attempts": 5,  # 最多重启5次
            },
            "source": {"data_path": "data/input.txt"},
            "sink": {},
        },
    )

    # 定义 DAG - 用户不关心容错
    (
        env.from_source(DemoFileSource, env.config["source"])
        .map(lambda x: x.strip())
        .sink(DemoTerminalSink, env.config["sink"])
    )

    # 提交 - 失败时自动重启
    env.submit()

    print("✅ Pipeline submitted with exponential backoff restart")


def example_3_user_no_fault_tolerance():
    """
    示例 3: 用户不配置容错（使用默认行为）

    """
    # 不配置 fault_tolerance，使用默认行为
    env = LocalEnvironment("simple_pipeline")

    # 正常定义和提交
    (
        env.from_source(DemoFileSource, {"data_path": "data.txt"})
        .map(lambda x: x.upper())
        .sink(DemoTerminalSink, {})
    )

    env.submit()

    print("✅ Pipeline submitted with default fault tolerance")


def example_4_user_yaml_config():
    """
    示例 4: 从 YAML 配置文件读取容错配置

    这是最常见的用法 - 配置在外部文件中管理。

    """
    # config.yaml 内容示例：
    # fault_tolerance:
    #   strategy: checkpoint
    #   checkpoint_interval: 30.0
    #   max_recovery_attempts: 5
    # source:
    #   file_path: data/input.txt
    # sink: {}

    config = _load_yaml_config("config/my_pipeline.yaml")

    # 容错配置从 YAML 文件读取
    env = LocalEnvironment("yaml_configured_pipeline", config=config)

    (
        env.from_source(DemoFileSource, config["source"])
        .map(lambda x: x.strip())
        .sink(DemoTerminalSink, config["sink"])
    )

    env.submit()

    print("✅ Pipeline submitted with YAML-configured fault tolerance")


# ============================================================================
# 开发者示例 - 扩展自定义容错策略
# ============================================================================


def example_5_developer_custom_strategy():
    """
    示例 5: 开发者实现自定义容错策略

    开发者可以遵循一个最小容错协议实现自己的容错逻辑。
    """

    class CircuitBreakerFaultHandler(FaultHandlerProtocol):
        """
        断路器容错策略

        当失败次数超过阈值时，打开断路器，停止重试一段时间。
        """

        def __init__(self, failure_threshold=5, timeout=60.0):
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.failure_counts = {}
            self.circuit_open = {}
            self.open_time = {}
            self.logger = None

        def handle_failure(self, task_id: str, error: Exception) -> bool:
            import time

            # 更新失败计数
            if task_id not in self.failure_counts:
                self.failure_counts[task_id] = 0
            self.failure_counts[task_id] += 1

            if self.logger:
                self.logger.warning(
                    f"Task {task_id} failed (count: {self.failure_counts[task_id]}): {error}"
                )

            # 检查是否应该打开断路器
            if self.failure_counts[task_id] >= self.failure_threshold:
                self.circuit_open[task_id] = True
                self.open_time[task_id] = time.time()

                if self.logger:
                    self.logger.error(
                        f"Circuit breaker opened for {task_id} "
                        f"(failures: {self.failure_counts[task_id]})"
                    )
                return False

            return self.recover(task_id)

        def can_recover(self, task_id: str) -> bool:
            import time

            # 如果断路器是打开的
            if self.circuit_open.get(task_id, False):
                # 检查是否已经超过超时时间
                if time.time() - self.open_time.get(task_id, 0) > self.timeout:
                    # 关闭断路器，重置计数
                    self.circuit_open[task_id] = False
                    self.failure_counts[task_id] = 0

                    if self.logger:
                        self.logger.info(f"Circuit breaker closed for {task_id}")

                    return True
                return False

            return self.failure_counts.get(task_id, 0) < self.failure_threshold

        def recover(self, task_id: str) -> bool:
            if self.logger:
                self.logger.info(f"Attempting to recover task {task_id}")

            # 实际的恢复逻辑
            # TODO: 实现具体的恢复策略
            # Issue URL: https://github.com/intellistream/SAGE/issues/933

            return True

    print("✅ Custom CircuitBreakerFaultHandler defined")
    print(
        "   Developers can implement the fault-handler protocol to create custom strategies"
    )


def example_6_developer_register_strategy():
    """
    示例 6: 开发者将自定义策略集成到系统

    步骤：
    1. 将自定义策略类放到 impl/ 目录
    2. 在 impl/__init__.py 中导出
    3. 在 factory.py 中添加创建逻辑
    4. 用户就可以通过配置使用了
    """

    # 步骤 1: 创建自定义策略文件
    # 例如: src/my_project/fault_tolerance/circuit_breaker.py

    # 步骤 2: 在 impl/__init__.py 添加导出
    # from my_project.fault_tolerance.circuit_breaker import CircuitBreakerFaultHandler
    # __all__ = [..., "CircuitBreakerFaultHandler"]

    # 步骤 3: 在 factory.py 添加创建逻辑
    # def create_fault_handler_from_config(config):
    #     strategy = config.get("strategy")
    #     if strategy == "circuit_breaker":
    #         return CircuitBreakerFaultHandler(
    #             failure_threshold=config.get("failure_threshold", 5),
    #             timeout=config.get("timeout", 60.0)
    #         )
    #     ...

    # 步骤 4: 用户现在可以通过配置使用
    # env = LocalEnvironment(
    #     "my_app",
    #     config={
    #         "fault_tolerance": {
    #             "strategy": "circuit_breaker",
    #             "failure_threshold": 3,
    #             "timeout": 30.0
    #         }
    #     }
    # )

    print("✅ Custom strategy integration steps:")
    print("   1. Create strategy class in impl/")
    print("   2. Export in impl/__init__.py")
    print("   3. Add creation logic in factory.py")
    print("   4. Users can now use it via config")


def example_7_developer_reference_implementations():
    """
    示例 7: 开发者参考现有实现

    查看 impl/ 目录下的实现来学习如何编写容错策略。
    """
    print("✅ Reference implementations in impl/:")
    print("   - checkpoint-like policies: periodic state snapshots")
    print("   - restart policies: fixed / exponential backoff")
    print("   - lifecycle hooks: startup, failure, shutdown")
    print("   - state managers: checkpoint persistence and restore")


# ============================================================================
# 运行所有示例
# ============================================================================


def run_user_examples():
    """运行应用用户示例"""
    print("\n" + "=" * 70)
    print("APPLICATION USER EXAMPLES - Fault Tolerance is Transparent")
    print("=" * 70 + "\n")

    print("Example 1: Checkpoint Strategy")
    print("-" * 70)
    example_1_user_checkpoint_strategy()

    print("\nExample 2: Restart Strategy with Exponential Backoff")
    print("-" * 70)
    example_2_user_restart_strategy()

    print("\nExample 3: No Explicit Fault Tolerance Configuration")
    print("-" * 70)
    example_3_user_no_fault_tolerance()

    print("\nExample 4: YAML Configuration")
    print("-" * 70)
    example_4_user_yaml_config()


def run_developer_examples():
    """运行开发者扩展示例"""
    print("\n" + "=" * 70)
    print("DEVELOPER EXAMPLES - Extending Fault Tolerance Strategies")
    print("=" * 70 + "\n")

    print("Example 5: Custom Circuit Breaker Strategy")
    print("-" * 70)
    example_5_developer_custom_strategy()

    print("\nExample 6: Integrating Custom Strategy into System")
    print("-" * 70)
    example_6_developer_register_strategy()

    print("\nExample 7: Reference Implementations")
    print("-" * 70)
    example_7_developer_reference_implementations()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "FAULT TOLERANCE EXAMPLES" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")

    run_user_examples()
    run_developer_examples()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")
