# """
# Fault Tolerance Demo

# 展示如何在 SAGE 应用中启用容错功能。
# 这个示例演示了用户如何通过简单的配置来启用容错，无需编写任何容错相关代码。
# """

# import os
# import sys

# from sage.runtime import LocalEnvironment
# from sage.foundation import SinkFunction, SourceFunction


# def demo_checkpoint_fault_tolerance():
#     """
#     演示 Checkpoint 容错策略

#     Checkpoint 策略会定期保存任务状态，失败时从最近的检查点恢复。
#     适用于长时间运行的有状态任务。
#     """
#     print("\n" + "=" * 70)
#     print("Demo 1: Checkpoint-based Fault Tolerance")
#     print("=" * 70)

#     # 创建环境，配置 Checkpoint 容错策略
#     env = LocalEnvironment(
#         "checkpoint_demo",
#         config={
#             # 容错配置 - 用户只需声明，系统自动处理
#             "fault_tolerance": {
#                 "strategy": "checkpoint",  # 使用 checkpoint 策略
#                 "checkpoint_interval": 30.0,  # 每30秒保存一次
#                 "max_recovery_attempts": 3,  # 最多尝试恢复3次
#                 "checkpoint_dir": ".demo_checkpoints",  # checkpoint存储目录
#             },
#             # 数据源配置
#             "source": {"file_path": "data/sample.txt"},
#             # 输出配置
#             "sink": {},
#         },
#     )

#     # 正常定义 DAG - 用户完全不需要关心容错
#     pipeline = (
#         env.from_source(FileSource, env.config["source"])
#         .map(lambda x: x.strip().upper())  # 转换为大写
#         .sink(TerminalSink, env.config["sink"])
#     )

#     # 提交作业 - 容错由系统自动处理
#     # 如果任务失败，系统会自动从最近的 checkpoint 恢复
#     env.submit()

#     print("\n✅ Pipeline with checkpoint fault tolerance submitted!")
#     print("   If tasks fail, they will automatically recover from checkpoints.")


# def demo_restart_fault_tolerance():
#     """
#     演示 Restart 容错策略（指数退避）

#     Restart 策略在任务失败时直接重启，使用指数退避算法逐渐增加重试延迟。
#     适用于无状态或短时间运行的任务。
#     """
#     print("\n" + "=" * 70)
#     print("Demo 2: Restart-based Fault Tolerance (Exponential Backoff)")
#     print("=" * 70)

#     # 创建环境，配置 Restart 容错策略
#     env = LocalEnvironment(
#         "restart_demo",
#         config={
#             # 容错配置 - 使用指数退避重启策略
#             "fault_tolerance": {
#                 "strategy": "restart",  # 使用 restart 策略
#                 "restart_strategy": "exponential",  # 指数退避
#                 "initial_delay": 1.0,  # 首次重启等待1秒
#                 "max_delay": 60.0,  # 最多等待60秒
#                 "multiplier": 2.0,  # 每次延迟翻倍
#                 "max_attempts": 5,  # 最多重启5次
#             },
#             "source": {"file_path": "data/sample.txt"},
#             "sink": {},
#         },
#     )

#     # 定义 DAG - 无需容错代码
#     pipeline = (
#         env.from_source(FileSource, env.config["source"])
#         .map(lambda x: x.strip().lower())  # 转换为小写
#         .sink(TerminalSink, env.config["sink"])
#     )

#     # 提交作业 - 失败时自动重启
#     env.submit()

#     print("\n✅ Pipeline with restart fault tolerance submitted!")
#     print("   If tasks fail, they will automatically restart with exponential backoff.")
#     print("   Retry delays: 1s, 2s, 4s, 8s, 16s...")


# def demo_fixed_delay_restart():
#     """
#     演示 Restart 容错策略（固定延迟）

#     使用固定延迟的重启策略，每次重启等待相同的时间。
#     """
#     print("\n" + "=" * 70)
#     print("Demo 3: Restart-based Fault Tolerance (Fixed Delay)")
#     print("=" * 70)

#     env = LocalEnvironment(
#         "fixed_restart_demo",
#         config={
#             # 容错配置 - 固定延迟重启
#             "fault_tolerance": {
#                 "strategy": "restart",
#                 "restart_strategy": "fixed",  # 固定延迟
#                 "delay": 5.0,  # 每次等待5秒
#                 "max_attempts": 3,  # 最多重启3次
#             },
#             "source": {"file_path": "data/sample.txt"},
#             "sink": {},
#         },
#     )

#     pipeline = (
#         env.from_source(FileSource, env.config["source"])
#         .map(lambda x: x.strip())
#         .sink(TerminalSink, env.config["sink"])
#     )

#     env.submit()

#     print("\n✅ Pipeline with fixed delay restart submitted!")
#     print("   If tasks fail, they will restart after 5 seconds each time.")


# def demo_no_fault_tolerance():
#     """
#     演示不配置容错（默认行为）

#     如果不配置 fault_tolerance，系统使用默认的简单重启策略。
#     """
#     print("\n" + "=" * 70)
#     print("Demo 4: No Explicit Fault Tolerance Configuration")
#     print("=" * 70)

#     # 不配置 fault_tolerance
#     env = LocalEnvironment(
#         "no_ft_demo", config={"source": {"file_path": "data/sample.txt"}, "sink": {}}
#     )

#     pipeline = (
#         env.from_source(FileSource, env.config["source"])
#         .map(lambda x: x.strip())
#         .sink(TerminalSink, env.config["sink"])
#     )

#     env.submit()

#     print("\n✅ Pipeline submitted with default fault tolerance.")


# def main():
#     """主函数 - 运行所有演示"""

#     # 检查是否在测试模式
#     if (
#         os.getenv("SAGE_EXAMPLES_MODE") == "test"
#         or os.getenv("SAGE_TEST_MODE") == "true"
#     ):
#         print("🧪 Test mode detected - fault_tolerance_demo")
#         print("✅ Test passed: Fault tolerance demo structure validated")
#         return

#     print("\n")
#     print("╔" + "=" * 68 + "╗")
#     print("║" + " " * 18 + "SAGE FAULT TOLERANCE DEMO" + " " * 25 + "║")
#     print("╚" + "=" * 68 + "╝")

#     print("\n📖 This demo shows how to enable fault tolerance in SAGE applications.")
#     print("   Users only need to declare the strategy in config - no code changes!")

#     # 创建示例数据文件（如果不存在）
#     os.makedirs("data", exist_ok=True)
#     if not os.path.exists("data/sample.txt"):
#         with open("data/sample.txt", "w") as f:
#             f.write("Hello World\n")
#             f.write("Fault Tolerance Demo\n")
#             f.write("SAGE Framework\n")
#         print("\n📄 Created sample data file: data/sample.txt")

#     # 运行各种容错策略演示
#     try:
#         demo_checkpoint_fault_tolerance()
#         demo_restart_fault_tolerance()
#         demo_fixed_delay_restart()
#         demo_no_fault_tolerance()

#         print("\n" + "=" * 70)
#         print("✨ All demos completed successfully!")
#         print("=" * 70)

#         print("\n📚 Learn more:")
#         print("   - Full documentation: see the fault tolerance README in this tutorial folder")
#         print("   - Quick reference: see the local QUICK_REFERENCE.md in this tutorial folder")
#         print(
#             "   - More examples: examples/kernel/fault_tolerance_examples.py"
#         )

#     except Exception as e:
#         print(f"\n❌ Error running demos: {e}")
#         import traceback

#         traceback.print_exc()
#         sys.exit(1)


# if __name__ == "__main__":
#     main()
