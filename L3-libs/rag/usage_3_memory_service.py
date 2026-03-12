"""Migration note for the retired memory-service middleware tutorial."""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本演示基于旧 memory middleware 的 DP unlearning 集成。")
    print("当前建议：使用核心 SAGE 维护业务状态，")
    print("如需长期记忆或向量记忆，请通过 isage-neuromem 等独立适配包接入。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
