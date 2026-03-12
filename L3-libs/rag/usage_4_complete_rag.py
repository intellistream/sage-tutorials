"""Migration note for the retired complete RAG + memory middleware tutorial."""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本依赖旧版 memory middleware 构建完整 RAG + unlearning 场景。")
    print("当前建议将检索编排保留在核心 SAGE 中，")
    print("并把记忆、向量库与隐私删除能力拆到独立适配包中实现。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
