"""Retired middleware tutorial note for legacy memory backend demos."""

from sage.foundation import CustomLogger


def main():
    print("此教程原本面向已退役的 neuromem/memory middleware 后端。")
    print("当前建议：使用核心 SAGE 数据流保存应用状态，")
    print("如需长期记忆或向量记忆，再接入独立适配包，例如 isage-neuromem。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
