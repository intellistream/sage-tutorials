#!/usr/bin/env python3
"""Migration note for the retired cross-modal SageDB search demo."""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本演示旧版跨模态 SageDB 检索接口。")
    print("当前建议：在核心 SAGE pipeline 外部使用独立多模态向量检索适配器，")
    print("并将检索结果作为普通数据结构接回 SAGE 数据流。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
