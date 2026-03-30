from sage.foundation import CustomLogger


def main():
    print("此教程原本依赖已退役的 agent/rag middleware 运行时。")
    print("当前建议：")
    print("1. 使用核心 SAGE pipeline 组织数据流。")
    print("2. 使用 isagellm 或 OpenAI-compatible 端点完成推理。")
    print("3. 将 tool registry、planner、memory 作为独立适配层接入。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
