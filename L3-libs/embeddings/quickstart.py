#!/usr/bin/env python3
"""Migration note for the retired multimodal SageDB quickstart."""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本演示旧版 multimodal SageDB API。")
    print("当前建议：将多模态向量检索能力通过独立适配包接入，")
    print("核心 SAGE 仅负责数据流编排、服务注册与调用。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
